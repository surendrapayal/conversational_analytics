import logging
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from conversational_analytics.models import AgentRequest, AgentResponse
from conversational_analytics.controller.agent_service import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["NLQ Agent"])


class QueryRequest(BaseModel):
    user_id: str
    query: str


@router.post("/chat", response_model=AgentResponse)
def query(
    body: QueryRequest,
    session_id: str = Header(..., description="Session ID for conversation memory"),
):
    """Accepts a natural language query and returns a SQL-backed response."""
    try:
        request = AgentRequest(
            user_id=body.user_id,
            session_id=session_id,
            query=body.query,
        )
        return run_agent(request)
    except Exception as e:
        logger.error(f"Agent error for session={session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
