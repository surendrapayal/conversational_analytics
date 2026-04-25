import logging
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from conversational_analytics.models import AgentState
from conversational_analytics.nlq_agent.nodes.nodes import agent_node, tools_node, response_formatter_node
from conversational_analytics.memory import get_checkpointer, get_long_term_store

logger = logging.getLogger(__name__)


def _should_continue(state: AgentState) -> Literal["tools", "response_formatter"]:
    """Routes to tools if the last AI message has tool calls, else to formatter."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        tool_names = [tc["name"] for tc in last.tool_calls]
        logger.debug(f"Routing to tools: {tool_names}")
        return "tools"
    logger.debug("Routing to response_formatter — no tool calls in last message")
    return "response_formatter"


def build_graph() -> StateGraph:
    logger.info("Building LangGraph graph...")
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.add_node("response_formatter", response_formatter_node)
    logger.debug("Graph nodes added: agent, tools, response_formatter")

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue)
    graph.add_edge("tools", "agent")
    graph.add_edge("response_formatter", END)
    logger.debug("Graph edges configured: agent→(tools|response_formatter), tools→agent, response_formatter→END")

    logger.info("Attaching Redis checkpointer (short-term memory)...")
    logger.info("Attaching PostgreSQL store (long-term memory)...")
    compiled = graph.compile(
        checkpointer=get_checkpointer(),
        store=get_long_term_store(),
    )
    logger.info("Graph compiled successfully with checkpointer and store")
    return compiled
