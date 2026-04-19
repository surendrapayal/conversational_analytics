from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from conversational_analytics.models import AgentState
from conversational_analytics.nlq_agent.nodes.nodes import agent_node, tools_node, response_formatter_node
from conversational_analytics.memory import get_checkpointer


def _should_continue(state: AgentState) -> Literal["tools", "response_formatter"]:
    """Routes to tools if the last AI message has tool calls, else to formatter."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "response_formatter"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.add_node("response_formatter", response_formatter_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue)
    graph.add_edge("tools", "agent")          # ReAct loop: tool result → agent
    graph.add_edge("response_formatter", END)

    # RedisSaver checkpointer — persists full graph state after every node
    return graph.compile(checkpointer=get_checkpointer())
