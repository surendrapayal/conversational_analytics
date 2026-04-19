import logging
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from conversational_analytics.models import AgentState
from conversational_analytics.nlq_agent.tools import get_sql_tools, get_system_message
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)

_tools = get_sql_tools()  # initialised once at module load


def agent_node(state: AgentState) -> dict:
    """Calls the LLM with tools bound and appends the AI response to messages."""
    response: AIMessage = get_llm().bind_tools(_tools).invoke(
        [get_system_message()] + state["messages"]
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
    result = ToolNode(_tools).invoke(state)

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


def response_formatter_node(state: AgentState) -> dict:
    """Extracts the final text response from the last AI message."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return {"final_response": _extract_text(msg.content)}
    return {"final_response": "I could not generate a response."}


def _extract_text(content) -> str:
    """Handles both plain string and list-of-parts content (Gemini thinking models)."""
    if isinstance(content, str):
        return content
    return " ".join(p["text"] for p in content if isinstance(p, dict) and p.get("type") == "text")
