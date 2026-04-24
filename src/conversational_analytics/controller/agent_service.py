import logging
import json
import time
from datetime import datetime, timezone
from collections.abc import Generator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from conversational_analytics.graph import build_graph
from conversational_analytics.models import AgentRequest, AgentResponse, AgentMetadata
from conversational_analytics.memory import log_query

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
            "messages": [HumanMessage(content=request.query)],
            "role": request.role,
        },
        config=config,
    )
    execution_ms = int((time.time() - start) * 1000)
    logger.info(f"Agent completed for user={request.user_id} session={request.session_id}")

    response_text = result["final_response"]
    vega_spec = result.get("vega_spec")
    tools_invoked = result.get("tools_invoked", [])
    sql_generated = next(
        (t for t in reversed(result.get("tool_results", [])) if "SELECT" in t.upper()), None
    )

    # persist query audit to long-term memory
    try:
        log_query(
            session_id=request.session_id,
            user_id=request.user_id,
            role=request.role,
            user_query=request.query,
            sql_generated=sql_generated,
            tools_invoked=tools_invoked,
            has_vega=vega_spec is not None,
            execution_ms=execution_ms,
        )
    except Exception as e:
        logger.warning(f"Failed to log query to long-term memory: {e}")

    return AgentResponse(
        response_text=response_text,
        vega_spec=vega_spec,
        metadata=AgentMetadata(
            tools_invoked=tools_invoked,
            thinking=result.get("thinking") or None,
        ),
    )


def _sse(event: str, payload: dict, session_id: str = "") -> str:
    """Formats a single SSE event with a JSON payload."""
    payload["session_id"] = session_id
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
            "messages": [HumanMessage(content=request.query)],
            "role": request.role,
        }

        # track state for audit log
        _tools_invoked: list[str] = []
        _tool_results: list[str] = []
        _final_response: str = ""
        _has_vega: bool = False

        for chunk in _graph.stream(input_state, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                if node_name == "agent":
                    for msg in state_update.get("messages", []):
                        if not isinstance(msg, AIMessage):
                            continue
                        if stream_mode == "verbose" and isinstance(msg.content, list):
                            for part in msg.content:
                                if isinstance(part, dict) and part.get("type") == "thinking" and part.get("thinking"):
                                    yield _sse("thinking", {"reasoning": part["thinking"].strip()}, request.session_id)
                        for tc in msg.tool_calls:
                            if stream_mode == "verbose":
                                yield _sse("tool_call", {"tool": tc["name"], "args": tc["args"]}, request.session_id)
                            else:
                                label = _TOOL_STEP_LABELS.get(tc["name"], "Processing")
                                yield _sse("step", {"message": label}, request.session_id)

                elif node_name == "tools":
                    for msg in state_update.get("messages", []):
                        if isinstance(msg, ToolMessage):
                            _tools_invoked.append(msg.name)
                            _tool_results.append(msg.content)
                            if stream_mode == "verbose":
                                yield _sse("tool_result", {"tool": msg.name, "output": msg.content}, request.session_id)

                elif node_name == "response_formatter":
                    final = state_update.get("final_response", "")
                    vega = state_update.get("vega_spec")
                    if final:
                        _final_response = final
                        _has_vega = vega is not None
                        yield _sse("response", {"text": final, "vega_spec": vega}, request.session_id)

        yield _sse("done", {"status": "completed"}, request.session_id)
        logger.info(f"Stream completed for user={request.user_id} session={request.session_id}")

        # persist audit log after stream completes
        try:
            sql_generated = next(
                (t for t in reversed(_tool_results) if "SELECT" in t.upper()), None
            )
            log_query(
                session_id=request.session_id,
                user_id=request.user_id,
                role=request.role,
                user_query=request.query,
                sql_generated=sql_generated,
                tools_invoked=_tools_invoked,
                has_vega=_has_vega,
                execution_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            logger.warning(f"Failed to log query audit: {e}")

    except Exception as e:
        logger.error(f"Error in stream_agent: {str(e)}", exc_info=True)
        yield _sse("error", {"message": str(e)}, request.session_id)
        yield _sse("done", {"status": "failed"}, request.session_id)
