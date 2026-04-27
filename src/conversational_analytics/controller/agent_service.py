import asyncio
import logging
import json
import time
from datetime import datetime, timezone
from collections.abc import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from conversational_analytics.graph import build_graph
from conversational_analytics.models import AgentRequest, AgentResponse, AgentMetadata
from conversational_analytics.memory import audit_writer, save_conversation_summary

logger = logging.getLogger(__name__)
logger.propagate = True

_graph = None  # initialised once via lifespan


async def init_graph():
    """Initialises the graph — called once at app startup via lifespan."""
    global _graph
    _graph = await build_graph()
    logger.info("Graph initialised and ready")


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


def _fire_log_agent_step(**kwargs) -> None:
    """Enqueues agent step — non-blocking, microseconds."""
    from conversational_analytics.config import get_settings
    cfg = get_settings()
    if cfg.long_term_memory_enabled:
        audit_writer.enqueue_agent_step(**kwargs)


def _process_chunk(chunk: dict, request: AgentRequest, state: dict) -> None:
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
                _fire_log_agent_step(
                    conversation_id=request.conversation_id,
                    session_id=request.session_id,
                    user_id=request.user_id,
                    step_number=state["step_number"],
                    step_type="llm_call",
                    output=llm_output,
                    token_usage=_extract_step_token_usage(msg),
                    duration_ms=int((time.time() - state["llm_call_start"]) * 1000),
                )

        elif node_name == "tools":
            for msg in state_update.get("messages", []):
                if isinstance(msg, ToolMessage):
                    state["tools_invoked"].append(msg.name)
                    state["step_number"] += 1
                    _fire_log_agent_step(
                        conversation_id=request.conversation_id,
                        session_id=request.session_id,
                        user_id=request.user_id,
                        step_number=state["step_number"],
                        step_type="tool_result",
                        tool_name=msg.name,
                        output=msg.content[:500],
                    )
                    state["llm_call_start"] = time.time()

        elif node_name == "response_formatter":
            final = state_update.get("final_response", "")
            vega = state_update.get("vega_spec")
            if final:
                state["final_response"] = final
                state["vega_spec"] = vega
                state["has_vega"] = vega is not None


async def _persist_audit(request: AgentRequest, state: dict, execution_ms: int) -> None:
    """Enqueues query log (non-blocking) and saves conversation summary (async) if enabled."""
    try:
        from conversational_analytics.config import get_settings
        cfg = get_settings()

        if cfg.long_term_memory_enabled:
            audit_writer.enqueue_query_log(
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
                stream_events=state.get("stream_events") or None,
                has_vega=state["has_vega"],
                execution_ms=execution_ms,
            )

        # Only save conversation summary if long-term memory is enabled
        if cfg.long_term_memory_enabled:
            await save_conversation_summary(
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
        "stream_events": [],
    }


async def run_agent(request: AgentRequest) -> AgentResponse:
    """Runs the agent asynchronously and returns a complete response."""
    start = time.time()
    config = {"configurable": {"thread_id": request.session_id}}
    state = _init_state()

    logger.info(f"run_agent started — user={request.user_id} session={request.session_id} conversation={request.conversation_id}")

    async for chunk in _graph.astream(_build_input_state(request), config=config, stream_mode="updates"):
        _process_chunk(chunk, request, state)

    execution_ms = int((time.time() - start) * 1000)
    logger.info(f"Agent completed — user={request.user_id} conversation={request.conversation_id} execution_ms={execution_ms}")
    asyncio.create_task(_persist_audit(request, state, execution_ms))

    return AgentResponse(
        response_text=state["final_response"],
        vega_spec=state["vega_spec"],
        metadata=AgentMetadata(
            session_id=request.session_id,
            conversation_id=request.conversation_id
        ),
    )


def _sse_collect(event: str, payload: dict, session_id: str, conversation_id: str, state: dict) -> str:
    """Formats SSE event, appends to state stream_events, and returns SSE string."""
    payload["session_id"] = session_id
    payload["conversation_id"] = conversation_id
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    state["stream_events"].append({"event": event, **payload})
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


_TOOL_STEP_LABELS = {
    "sql_db_list_tables": "Identifying available data sources",
    "sql_db_schema": "Analysing data structure",
    "sql_db_query_checker": "Validating query",
    "sql_db_query": "Retrieving data",
}


async def stream_agent(request: AgentRequest, stream_mode: str = "standard") -> AsyncGenerator[str, None]:
    """Streams agent execution as Server-Sent Events using async generator."""
    start = time.time()
    state = _init_state()
    try:
        logger.info(f"stream_agent started — user={request.user_id} session={request.session_id} conversation={request.conversation_id} mode={stream_mode}")
        config = {"configurable": {"thread_id": request.session_id}}

        async for chunk in _graph.astream(_build_input_state(request), config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                _process_chunk({node_name: state_update}, request, state)

                if node_name == "agent":
                    for msg in state_update.get("messages", []):
                        if not isinstance(msg, AIMessage):
                            continue
                        if stream_mode == "verbose" and isinstance(msg.content, list):
                            for part in msg.content:
                                if isinstance(part, dict) and part.get("type") == "thinking" and part.get("thinking"):
                                    yield _sse_collect("thinking", {"reasoning": part["thinking"].strip()}, request.session_id, request.conversation_id, state)
                        for tc in msg.tool_calls:
                            if stream_mode == "verbose":
                                yield _sse_collect("tool_call", {"tool": tc["name"], "args": tc["args"]}, request.session_id, request.conversation_id, state)
                            else:
                                label = _TOOL_STEP_LABELS.get(tc["name"], "Processing")
                                yield _sse_collect("step", {"message": label}, request.session_id, request.conversation_id, state)

                elif node_name == "tools":
                    if stream_mode == "verbose":
                        for msg in state_update.get("messages", []):
                            if isinstance(msg, ToolMessage):
                                yield _sse_collect("tool_result", {"tool": msg.name, "output": msg.content}, request.session_id, request.conversation_id, state)

                elif node_name == "response_formatter":
                    if state["final_response"]:
                        yield _sse_collect("response", {"text": state["final_response"], "vega_spec": state["vega_spec"]}, request.session_id, request.conversation_id, state)

        yield _sse_collect("done", {"status": "completed"}, request.session_id, request.conversation_id, state)
        execution_ms = int((time.time() - start) * 1000)
        logger.info(f"Stream completed — user={request.user_id} conversation={request.conversation_id} execution_ms={execution_ms}")
        asyncio.create_task(_persist_audit(request, state, execution_ms))

    except Exception as e:
        logger.error(f"Error in stream_agent: {str(e)}", exc_info=True)
        yield _sse_collect("error", {"message": str(e)}, request.session_id, request.conversation_id, state)
        yield _sse_collect("done", {"status": "failed"}, request.session_id, request.conversation_id, state)
