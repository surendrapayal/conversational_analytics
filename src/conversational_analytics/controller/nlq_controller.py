import uuid
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
    stream_mode: str = "standard"  # standard | verbose


@router.post("/chat", response_model=AgentResponse)
def query(
    body: QueryRequest,
    session_id: str = Header(..., description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role: admin | general_manager | location_manager | staff"),
):
    """Accepts a natural language query and returns a SQL-backed response."""
    conversation_id = str(uuid.uuid4())  # always generate a new UUID per stream request
    try:
        request = AgentRequest(
            user_id=body.user_id,
            session_id=session_id,
            query=body.query,
            role=role,
            conversation_id=conversation_id,
        )
        return run_agent(request)
    except Exception as e:
        logger.error(f"Agent error for session={session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
def stream(
    body: QueryRequest,
    session_id: str = Header(..., description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role: admin | general_manager | location_manager | staff"),
):
    """Streams agent execution as Server-Sent Events (SSE).
    Events: thinking | tool_call | tool_result | response | done
    """
    try:
        conversation_id = str(uuid.uuid4())  # always generate a new UUID per stream request
        logger.info(f"Stream request received: user={body.user_id}, session={session_id}, role={role}, conversation={conversation_id}")
        request = AgentRequest(
            user_id=body.user_id,
            session_id=session_id,
            query=body.query,
            role=role,
            conversation_id=conversation_id,
        )
        return StreamingResponse(
            stream_agent(request, stream_mode=body.stream_mode),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no"},
        )
    except Exception as e:
        logger.error(f"Stream error for session={session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
