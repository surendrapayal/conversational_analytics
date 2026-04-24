import json
import logging
import re
import time
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore
from conversational_analytics.models import AgentState
from conversational_analytics.nlq_agent.tools import get_sql_tools, get_system_message
from conversational_analytics.config import get_settings
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)

_tools = get_sql_tools()  # default tools - no role


def agent_node(state: AgentState, store: BaseStore) -> dict:
    """Calls the LLM with tools bound. Reads long-term memory from store."""
    cfg = get_settings()
    tools_invoked = state.get("tools_invoked", [])
    role = state.get("role")
    user_id = state.get("user_id") or ""
    tools = get_sql_tools(role)
    system_msg = get_system_message(role)

    # ── recall long-term memory (only on first agent call, not on ReAct loops) ──
    memory_context = ""
    if user_id and store and not tools_invoked:  # tools_invoked is empty only on first call
        try:
            memories = store.search(("conversation_history", user_id), limit=5)
            if memories:
                history = "\n".join(
                    f"- Q: {m.value.get('query', '')} | A: {m.value.get('response', '')[:100]}..."
                    for m in memories
                )
                memory_context = f"\n\nRecent conversation history:\n{history}"
                logger.info(f"Recalled {len(memories)} past turns for user={user_id}")
        except Exception as e:
            logger.debug(f"Could not retrieve long-term memory: {e}")

    enriched_system = SystemMessage(
        content=system_msg.content + memory_context
    ) if memory_context else system_msg

    # guard: if max iterations reached, force the LLM to respond without tools
    if len(tools_invoked) >= cfg.agent_max_iterations:
        logger.warning(f"Max iterations ({cfg.agent_max_iterations}) reached - forcing final response")
        response: AIMessage = get_llm().invoke(
            [enriched_system]
            + state["messages"]
            + [HumanMessage(content="You have used the maximum number of tool calls. Based on what you have found so far, provide your final answer now. Do not call any more tools.")]
        )
    else:
        response: AIMessage = get_llm().bind_tools(tools).invoke(
            [enriched_system] + state["messages"]
        )

    thinking = response.additional_kwargs.get("thinking", "") if hasattr(response, "additional_kwargs") else ""
    step = f"Agent responded: {response.content[:100]}..." if response.content else "Agent invoked tools"
    logger.info(step)

    return {
        "messages": [response],
        "intermediate_steps": state.get("intermediate_steps", []) + [step],
        "thinking": thinking,
    }


def tools_node(state: AgentState) -> dict:
    """Runs ToolNode and tracks which tools were invoked and their results."""
    role = state.get("role")
    tools = get_sql_tools(role)
    result = ToolNode(tools).invoke(state)

    tool_messages: list[ToolMessage] = [m for m in result.get("messages", []) if isinstance(m, ToolMessage)]
    tools_invoked = [m.name for m in tool_messages]
    tool_results = [m.content for m in tool_messages]
    logger.info(f"Tools executed: {tools_invoked}")

    return {
        "messages": tool_messages,
        "tool_results": state.get("tool_results", []) + tool_results,
        "tools_invoked": state.get("tools_invoked", []) + tools_invoked,
        "intermediate_steps": state.get("intermediate_steps", []) + [f"Tools called: {tools_invoked}"],
    }


def response_formatter_node(state: AgentState, store: BaseStore) -> dict:
    """Extracts the final text response and optional Vega spec. Writes to long-term store."""
    for msg in reversed(state["messages"]):
        if not isinstance(msg, AIMessage) or not msg.content:
            continue
        extracted = _extract_text(msg.content)
        text, vega_spec = _extract_vega_spec(extracted)
        if text or vega_spec:
            logger.info(f"Extracted final response: {len(text)} chars, vega_spec: {vega_spec is not None}")

            # ── write Q&A turn to long-term store (once, after final response) ──
            user_id = state.get("user_id") or ""
            if user_id and store:
                try:
                    store.put(
                        ("conversation_history", user_id),
                        f"turn_{int(time.time())}",
                        {
                            "query": state.get("user_input", ""),
                            "response": text[:500],
                            "tools_invoked": state.get("tools_invoked", []),
                            "has_vega": vega_spec is not None,
                            "role": state.get("role"),
                        },
                    )
                    logger.info(f"Saved conversation turn to long-term store for user={user_id}")
                except Exception as e:
                    logger.debug(f"Could not write to long-term memory: {e}")

            return {"final_response": text, "vega_spec": vega_spec}

    logger.warning("No final response found in messages")
    return {"final_response": "I could not generate a response.", "vega_spec": None}


def _extract_vega_spec(text: str) -> tuple[str, dict | None]:
    """Extracts a vega code block from the response text."""
    pattern = r"```vega\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if not match:
        return text, None
    try:
        parsed = json.loads(match.group(1).strip())
        if isinstance(parsed, dict) and "vega_spec" in parsed and len(parsed) == 1:
            parsed = parsed["vega_spec"]
        if not isinstance(parsed, dict) or "mark" not in parsed:
            logger.warning("Parsed vega block does not look like a valid Vega-Lite spec")
            return text, None
        clean_text = re.sub(pattern, "", text).strip()
        return clean_text, parsed
    except json.JSONDecodeError:
        logger.warning("Found vega block but failed to parse as JSON")
        return text, None


def _extract_text(content) -> str:
    """Handles both plain string and list-of-parts content (Gemini thinking models)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part["text"] for part in content
            if isinstance(part, dict) and part.get("type") == "text" and part.get("text")
        )
    return str(content) if content else ""
