import logging
from langchain_core.messages import HumanMessage
from conversational_analytics.graph import build_graph
from conversational_analytics.models import AgentRequest, AgentResponse, AgentMetadata

logger = logging.getLogger(__name__)

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
