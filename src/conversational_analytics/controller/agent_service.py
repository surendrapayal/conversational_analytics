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
logger.propagate = True

_graph = build_graph()  # built once, checkpointer is attached


def _build_input_state(request: AgentRequest) -> dict:
    """Builds the initial graph state from a request."""
    return {
        "user_input": request.query,
        "user_id": request.user_id,
        "conversation_id": request.conversation_id,
        "messages": [HumanMessage(content=request.query)],
        "role": request.role,
        "prompt": None,
    }


def _extract_step_token_usage(msg: AIMessage) -> dict | None:
    """Extracts per-step token usage from an AIMessage."""
    if not msg.usage_metadata:
        return None
    um = msg.usage_metadata
    return {
        "input_tokens": um.get("input_tokens", 0),
        "output_tokens": um.get("output_tokens", 0),
        "total_tokens": um.get("total_tokens", 0),
        "reasoning_tokens": um.get("output_token_details", {}).get("reasoning", 0),
    }


def _process_chunk(
    chunk: dict,
    request: AgentRequest,
    state: dict,
) -> None:
    """Processes a single graph stream chunk — updates state and logs agent steps."""
    for node_name, state_update in chunk.items():
        if node_name == "agent":
            if state_update.get("token_usage"):
                state["token_usage"] = state_update["token_usage"]
            if state_update.get("prompt") and state["prompt"] is None:
                state["prompt"] = state_update["prompt"]
            for msg in state_update.get("messages", []):
                if not isinstance(msg, AIMessage):
                    continue
                for tc in msg.tool_calls:
                    if tc["name"] == "sql_db_query" and tc["args"].get("query"):
                        state["sql_generated"] = tc["args"]["query"]
                state["step_number"] += 1
                tool_names = [tc["name"] for tc in msg.tool_calls]
                llm_output = f"Decided to call: {tool_names}" if tool_names else "Generated final response"
                try:
                    log_agent_step(
                        conversation_id=request.conversation_id,
                        session_id=request.session_id,
                        user_id=request.user_id,
                        step_number=state["step_number"],
                        step_type="llm_call",
                        output=llm_output,
                        token_usage=_extract_step_token_usage(msg),
                        duration_ms=int((time.time() - state["llm_call_start"]) * 1000),
                    )
                except Exception as e:
                    logger.debug(f"Failed to log llm_call step: {e}")

        elif node_name == "tools":
            for msg in state_update.get("messages", []):
                if isinstance(msg, ToolMessage):
                    state["tools_invoked"].append(msg.name)
                    state["step_number"] += 1
                    try:
                        log_agent_step(
                            conversation_id=request.conversation_id,
                            session_id=request.session_id,
                            user_id=request.user_id,
                            step_number=state["step_number"],
                            step_type="tool_result",
                            tool_name=msg.name,
                            output=msg.content[:500],
                        )
                    except Exception as e:
                        logger.debug(f"Failed to log tool_result step: {e}")
                    state["llm_call_start"] = time.time()

        elif node_name == "response_formatter":
            final = state_update.get("final_response", "")
            vega = state_update.get("vega_spec")
            if final:
                state["final_response"] = final
                state["vega_spec"] = vega
                state["has_vega"] = vega is not None


def _persist_audit(request: AgentRequest, state: dict, execution_ms: int) -> None:
    """Persists query log and conversation summary after graph completes."""
    try:
        log_query(
            conversation_id=request.conversation_id,
            session_id=request.session_id,
            user_id=request.user_id,
            role=request.role,
            user_query=request.query,
            prompt=state["prompt"],
            sql_generated=state["sql_generated"],
            tools_invoked=state["tools_invoked"],
            agent_response=state["final_response"],
            vega_spec=state["vega_spec"],
            token_usage=state["token_usage"],
            has_vega=state["has_vega"],
            execution_ms=execution_ms,
        )
        save_conversation_summary(
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_id=request.conversation_id,
            user_query=request.query,
            response_text=state["final_response"],
            role=request.role,
        )
    except Exception as e:
        logger.warning(f"Failed to persist audit: {e}")


def _init_state() -> dict:
    """Returns a fresh tracking state dict."""
    return {
        "tools_invoked": [],
        "final_response": "",
        "vega_spec": None,
        "token_usage": None,
        "prompt": None,
        "sql_generated": None,
        "has_vega": False,
        "step_number": 0,
        "llm_call_start": time.time(),
    }


def run_agent(request: AgentRequest) -> AgentResponse:
    start = time.time()
    config = {"configurable": {"thread_id": request.session_id}}
    state = _init_state()

    logger.info(f"run_agent started for user_id={request.user_id} session_id={request.session_id} conversation_id={request.conversation_id}")

    for chunk in _graph.stream(_build_input_state(request), config=config, stream_mode="updates"):
        _process_chunk(chunk, request, state)

    execution_ms = int((time.time() - start) * 1000)
    logger.info(f"Agent completed for user_id={request.user_id} session_id={request.session_id} conversation_id={request.conversation_id} execution_time={execution_ms}ms")
    _persist_audit(request, state, execution_ms)

    return AgentResponse(
        response_text=state["final_response"],
        vega_spec=state["vega_spec"],
        metadata=AgentMetadata(
            conversation_id=request.conversation_id,
            # tools_invoked=state["tools_invoked"],
            # token_usage=state["token_usage"],
        ),
    )


def _sse(event: str, payload: dict, session_id: str = "", conversation_id: str = "") -> str:
    """Formats a single SSE event with a JSON payload."""
    payload["session_id"] = session_id
    payload["conversation_id"] = conversation_id
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    logger.debug(f"SSE event: {event} payload: {payload}")
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


_TOOL_STEP_LABELS = {
    "sql_db_list_tables": "Identifying available data sources",
    "sql_db_schema": "Analysing data structure",
    "sql_db_query_checker": "Validating query",
    "sql_db_query": "Retrieving data",
}


def stream_agent(request: AgentRequest, stream_mode: str = "standard") -> Generator[str, None, None]:
    """Streams agent execution as Server-Sent Events.

    stream_mode:
      standard - business-friendly output: step progress + final response only
      verbose  - full internal details: thinking, tool names, args, raw DB output
    """
    start = time.time()
    try:
        logger.info(f"stream_agent started for user_id={request.user_id} session_id={request.session_id} conversation_id={request.conversation_id} stream_mode={stream_mode}")
        config = {"configurable": {"thread_id": request.session_id}}
        state = _init_state()

        for chunk in _graph.stream(_build_input_state(request), config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                # process chunk for logging (shared logic)
                _process_chunk({node_name: state_update}, request, state)

                # SSE output
                if node_name == "agent":
                    for msg in state_update.get("messages", []):
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
                    if stream_mode == "verbose":
                        for msg in state_update.get("messages", []):
                            if isinstance(msg, ToolMessage):
                                yield _sse("tool_result", {"tool": msg.name, "output": msg.content}, request.session_id, request.conversation_id)

                elif node_name == "response_formatter":
                    if state["final_response"]:
                        yield _sse("response", {"text": state["final_response"], "vega_spec": state["vega_spec"]}, request.session_id, request.conversation_id)

        yield _sse("done", {"status": "completed"}, request.session_id, request.conversation_id)
        logger.info(f"Stream completed for user_id={request.user_id} session_id={request.session_id} conversation_id={request.conversation_id} execution_time={execution_ms}ms")
        _persist_audit(request, state, int((time.time() - start) * 1000))

    except Exception as e:
        logger.error(f"Error in stream_agent: {str(e)}", exc_info=True)
        yield _sse("error", {"message": str(e)}, request.session_id, request.conversation_id)
        yield _sse("done", {"status": "failed"}, request.session_id, request.conversation_id)
