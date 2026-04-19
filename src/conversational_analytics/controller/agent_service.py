import logging
import json
import sys
from datetime import datetime, timezone
from collections.abc import Generator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from conversational_analytics.graph import build_graph
from conversational_analytics.models import AgentRequest, AgentResponse, AgentMetadata

logger = logging.getLogger(__name__)
logger.propagate = True  # Ensure logs propagate to root logger

_graph = build_graph()  # built once, checkpointer is attached


def run_agent(request: AgentRequest) -> AgentResponse:
    config = {"configurable": {"thread_id": request.session_id}}
    result = _graph.invoke(
        {"user_input": request.query, "messages": [HumanMessage(content=request.query)]},
        config=config,
    )
    logger.info(f"Agent completed for user={request.user_id} session={request.session_id}")
    return AgentResponse(
        response_text=result["final_response"],
        metadata=AgentMetadata(
            tools_invoked=result.get("tools_invoked", []),
            thinking=result.get("thinking") or None,
        ),
    )


def _sse(event: str, payload: dict, session_id: str = "") -> str:
    """Formats a single SSE event with a JSON payload."""
    payload["session_id"] = session_id
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def stream_agent(request: AgentRequest) -> Generator[str, None, None]:
    """Streams agent execution as Server-Sent Events.

    Events emitted:
      thinking   — Gemini internal reasoning text
      tool_call  — tool name + args the agent decided to invoke
      tool_result — raw output returned by the tool
      response   — final formatted answer
      done       — stream complete
    """
    try:
        logger.info(f"stream_agent started for user={request.user_id} session={request.session_id}")
        config = {"configurable": {"thread_id": request.session_id}}
        input_state = {"user_input": request.query, "messages": [HumanMessage(content=request.query)]}

        for chunk in _graph.stream(input_state, config=config, stream_mode="updates"):
            logger.info(f"chunk received: {chunk}")
            for node_name, state_update in chunk.items():
                logger.info(f"Processing node '{node_name}'")
                if node_name == "agent":
                    for msg in state_update.get("messages", []):
                        if not isinstance(msg, AIMessage):
                            continue

                        # 1. emit Gemini thinking/reasoning text from content parts
                        if isinstance(msg.content, list):
                            for part in msg.content:
                                if isinstance(part, dict) and part.get("type") == "thinking" and part.get("thinking"):
                                    logger.info("Yielding thinking event")
                                    yield _sse("thinking", {"reasoning": part["thinking"].strip()}, request.session_id)

                        # 2. emit each tool call the agent decided to make
                        for tc in msg.tool_calls:
                            logger.info(f"Yielding tool_call event: {tc['name']}")
                            yield _sse("tool_call", {"tool": tc["name"], "args": tc["args"]}, request.session_id)

                elif node_name == "tools":
                    for msg in state_update.get("messages", []):
                        if isinstance(msg, ToolMessage):
                            # 3. emit the raw tool output
                            logger.info(f"Yielding tool_result event: {msg.name}")
                            yield _sse("tool_result", {"tool": msg.name, "output": msg.content}, request.session_id)

                elif node_name == "response_formatter":
                    final = state_update.get("final_response", "")
                    if final:
                        logger.info(f"Yielding response event with {len(final)} chars")
                        yield _sse("response", {"text": final}, request.session_id)

        logger.info("Yielding done event")
        yield _sse("done", {"status": "completed"}, request.session_id)
        logger.info(f"Stream completed successfully for user={request.user_id} session={request.session_id}")
        
    except Exception as e:
        logger.error(f"Error in stream_agent: {str(e)}", exc_info=True)
        yield _sse("error", {"message": str(e)}, request.session_id)
        yield _sse("done", {"status": "failed"}, request.session_id)
