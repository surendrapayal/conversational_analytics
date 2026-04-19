import logging
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from conversational_analytics.models import AgentRequest, AgentResponse
from conversational_analytics.controller.agent_service import run_agent, stream_agent

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
        request = AgentRequest(user_id=body.user_id, session_id=session_id, query=body.query)
        return run_agent(request)
    except Exception as e:
        logger.error(f"Agent error for session={session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
def stream(
    body: QueryRequest,
    session_id: str = Header(..., description="Session ID for conversation memory"),
):
    """Streams agent execution as Server-Sent Events (SSE).
    Events: thinking | tool_call | tool_result | response | done
    """
    try:
        logger.info(f"Stream request received: user={body.user_id}, session={session_id}")
        request = AgentRequest(user_id=body.user_id, session_id=session_id, query=body.query)
        return StreamingResponse(
            stream_agent(request),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no"}  # Disable proxy buffering
        )
    except Exception as e:
        logger.error(f"Stream error for session={session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
