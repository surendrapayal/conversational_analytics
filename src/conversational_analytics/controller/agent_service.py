import logging
import json
import time
from datetime import datetime, timezone
from collections.abc import Generator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from conversational_analytics.graph import build_graph
from conversational_analytics.models import AgentRequest, AgentResponse, AgentMetadata
from conversational_analytics.memory import log_query, save_conversation_summary, log_agent_step

logger = logging.getLogger(__name__)
logger.propagate = True  # Ensure logs propagate to root logger

_graph = build_graph()  # built once, checkpointer is attached


def run_agent(request: AgentRequest) -> AgentResponse:
    start = time.time()
    config = {"configurable": {"thread_id": request.session_id}}

    result = _graph.invoke(
        {
            "user_input": request.query,
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            "messages": [HumanMessage(content=request.query)],
            "role": request.role,
            "prompt": None,
        },
        config=config,
    )
    execution_ms = int((time.time() - start) * 1000)
    logger.info(f"Agent completed for user={request.user_id} session={request.session_id}")

    response_text = result["final_response"]
    vega_spec = result.get("vega_spec")
    tools_invoked = result.get("tools_invoked", [])
    token_usage = result.get("token_usage")
    prompt = result.get("prompt")
    # extract SQL from messages — look in AIMessage tool_calls args for sql_db_query
    sql_generated = None
    for msg in reversed(result.get("messages", [])):
        if hasattr(msg, "tool_calls"):
            for tc in msg.tool_calls:
                if tc["name"] == "sql_db_query" and tc["args"].get("query"):
                    sql_generated = tc["args"]["query"]
                    break
        if sql_generated:
            break

    try:
        log_query(
            conversation_id=request.conversation_id,
            session_id=request.session_id,
            user_id=request.user_id,
            role=request.role,
            user_query=request.query,
            prompt=prompt,
            sql_generated=sql_generated,
            tools_invoked=tools_invoked,
            agent_response=response_text,
            vega_spec=vega_spec,
            token_usage=token_usage,
            has_vega=vega_spec is not None,
            execution_ms=execution_ms,
        )
        save_conversation_summary(
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_id=request.conversation_id,
            user_query=request.query,
            response_text=response_text,
            role=request.role,
        )
    except Exception as e:
        logger.warning(f"Failed to log query to long-term memory: {e}")

    return AgentResponse(
        response_text=response_text,
        vega_spec=vega_spec,
        metadata=AgentMetadata(
            conversation_id=request.conversation_id,
            tools_invoked=tools_invoked,
            thinking=result.get("thinking") or None,
            token_usage=token_usage,
        ),
    )


def _sse(event: str, payload: dict, session_id: str = "", conversation_id: str = "") -> str:
    """Formats a single SSE event with a JSON payload."""
    payload["session_id"] = session_id
    payload["conversation_id"] = conversation_id
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


# Maps internal SQL tool names to business-friendly step descriptions
_TOOL_STEP_LABELS = {
    "sql_db_list_tables": "Identifying available data sources",
    "sql_db_schema": "Analysing data structure",
    "sql_db_query_checker": "Validating query",
    "sql_db_query": "Retrieving data",
}


def stream_agent(request: AgentRequest, stream_mode: str = "standard") -> Generator[str, None, None]:
    """Streams agent execution as Server-Sent Events.

    stream_mode:
      standard - business-friendly output (default): step progress + final response only
      verbose  - full internal details: thinking, tool names, args, raw DB output
    """
    start = time.time()
    try:
        logger.info(f"stream_agent started for user={request.user_id} session={request.session_id}")
        config = {"configurable": {"thread_id": request.session_id}}
        input_state = {
            "user_input": request.query,
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            "messages": [HumanMessage(content=request.query)],
            "role": request.role,
            "prompt": None,
        }

        # track state for audit log
        _tools_invoked: list[str] = []
        _tool_results: list[str] = []
        _final_response: str = ""
        _vega_spec: dict | None = None
        _token_usage: dict | None = None
        _prompt: str | None = None
        _sql_generated: str | None = None
        _has_vega: bool = False
        _step_number: int = 0
        _llm_call_start: float = time.time()

        for chunk in _graph.stream(input_state, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                if node_name == "agent":
                    if state_update.get("token_usage"):
                        _token_usage = state_update["token_usage"]
                    if state_update.get("prompt") and _prompt is None:
                        _prompt = state_update["prompt"]
                    for msg in state_update.get("messages", []):
                        if not isinstance(msg, AIMessage):
                            continue
                        # capture SQL from tool call args
                        for tc in msg.tool_calls:
                            if tc["name"] == "sql_db_query" and tc["args"].get("query"):
                                _sql_generated = tc["args"]["query"]
                        # log llm_call step
                        _step_number += 1
                        step_token_usage = None
                        if msg.usage_metadata:
                            um = msg.usage_metadata
                            step_token_usage = {
                                "input_tokens": um.get("input_tokens", 0),
                                "output_tokens": um.get("output_tokens", 0),
                                "total_tokens": um.get("total_tokens", 0),
                                "reasoning_tokens": um.get("output_token_details", {}).get("reasoning", 0),
                            }
                        tool_names = [tc["name"] for tc in msg.tool_calls]
                        llm_output = f"Decided to call: {tool_names}" if tool_names else "Generated final response"
                        try:
                            log_agent_step(
                                conversation_id=request.conversation_id,
                                session_id=request.session_id,
                                user_id=request.user_id,
                                step_number=_step_number,
                                step_type="llm_call",
                                output=llm_output,
                                token_usage=step_token_usage,
                                duration_ms=int((time.time() - _llm_call_start) * 1000),
                            )
                        except Exception as e:
                            logger.debug(f"Failed to log llm_call step: {e}")
                        if not isinstance(msg, AIMessage):
                            continue
                        if stream_mode == "verbose" and isinstance(msg.content, list):
                            for part in msg.content:
                                if isinstance(part, dict) and part.get("type") == "thinking" and part.get("thinking"):
                                    yield _sse("thinking", {"reasoning": part["thinking"].strip()}, request.session_id, request.conversation_id)
                        for tc in msg.tool_calls:
                            if stream_mode == "verbose":
                                yield _sse("tool_call", {"tool": tc["name"], "args": tc["args"]}, request.session_id, request.conversation_id)
                            else:
                                label = _TOOL_STEP_LABELS.get(tc["name"], "Processing")
                                yield _sse("step", {"message": label}, request.session_id, request.conversation_id)

                elif node_name == "tools":
                    for msg in state_update.get("messages", []):
                        if isinstance(msg, ToolMessage):
                            _tools_invoked.append(msg.name)
                            _tool_results.append(msg.content)
                            # log tool_call and tool_result steps
                            _step_number += 1
                            tool_input = None
                            # find matching tool call args from previous AIMessage
                            try:
                                log_agent_step(
                                    conversation_id=request.conversation_id,
                                    session_id=request.session_id,
                                    user_id=request.user_id,
                                    step_number=_step_number,
                                    step_type="tool_result",
                                    tool_name=msg.name,
                                    output=msg.content[:500],  # truncate large outputs
                                )
                            except Exception as e:
                                logger.debug(f"Failed to log tool_result step: {e}")
                            _llm_call_start = time.time()  # reset timer for next LLM call
                            if stream_mode == "verbose":
                                yield _sse("tool_result", {"tool": msg.name, "output": msg.content}, request.session_id, request.conversation_id)

                elif node_name == "response_formatter":
                    final = state_update.get("final_response", "")
                    vega = state_update.get("vega_spec")
                    if final:
                        _final_response = final
                        _vega_spec = vega
                        _has_vega = vega is not None
                        yield _sse("response", {"text": final, "vega_spec": vega}, request.session_id, request.conversation_id)

        yield _sse("done", {"status": "completed"}, request.session_id, request.conversation_id)
        logger.info(f"Stream completed for user={request.user_id} session={request.session_id} conversation={request.conversation_id}")

        # persist audit log and session summary after stream completes
        try:
            log_query(
                conversation_id=request.conversation_id,
                session_id=request.session_id,
                user_id=request.user_id,
                role=request.role,
                user_query=request.query,
                prompt=_prompt,
                sql_generated=_sql_generated,
                tools_invoked=_tools_invoked,
                agent_response=_final_response,
                vega_spec=_vega_spec,
                token_usage=_token_usage,
                has_vega=_has_vega,
                execution_ms=int((time.time() - start) * 1000),
            )
            save_conversation_summary(
                user_id=request.user_id,
                session_id=request.session_id,
                conversation_id=request.conversation_id,
                user_query=request.query,
                response_text=_final_response,
                role=request.role,
            )
        except Exception as e:
            logger.warning(f"Failed to log query audit: {e}")

    except Exception as e:
        logger.error(f"Error in stream_agent: {str(e)}", exc_info=True)
        yield _sse("error", {"message": str(e)}, request.session_id, request.conversation_id)
        yield _sse("done", {"status": "failed"}, request.session_id, request.conversation_id)
