import uuid
import logging
import nh3
from typing import Literal
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from conversational_analytics.models import AgentRequest, AgentResponse
from conversational_analytics.controller.agent_service import run_agent, stream_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["NLQ Agent"])

QUERY_MIN_LENGTH = 5
QUERY_MAX_LENGTH = 1000


def sanitize_input(value: str, field_name: str) -> str:
    """Validates and sanitizes input — rejects HTML/script content."""
    sanitized = nh3.clean(value, tags=set()).strip()
    if value.strip() != sanitized:
        raise ValueError(f"Invalid characters detected in '{field_name}': HTML/script not allowed.")
    return sanitized


class QueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=QUERY_MIN_LENGTH, max_length=QUERY_MAX_LENGTH)
    stream_mode: Literal["standard", "verbose"] = Field(default="standard")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        sanitized = sanitize_input(v, "query")
        if len(sanitized) < QUERY_MIN_LENGTH:
            raise ValueError(f"Query must be at least {QUERY_MIN_LENGTH} characters")
        if len(sanitized) > QUERY_MAX_LENGTH:
            raise ValueError(f"Query must not exceed {QUERY_MAX_LENGTH} characters")
        return sanitized

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        return sanitize_input(v, "user_id")


@router.post("/chat", response_model=AgentResponse)
async def query(
    body: QueryRequest,
    session_id: str = Header(None, description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role"),
):
    """Accepts a natural language query and returns a SQL-backed response."""
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"No session_id provided — generated session_id={session_id}")

    conversation_id = str(uuid.uuid4())
    logger.info(f"Chat request: query_len={len(body.query)} mode={body.stream_mode}")
    try:
        request = AgentRequest(
            user_id=body.user_id,
            session_id=session_id,
            query=body.query,
            role=role,
            conversation_id=conversation_id,
        )
        return await run_agent(request)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream(
    body: QueryRequest,
    session_id: str = Header(None, description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role"),
):
    """Streams agent execution as Server-Sent Events (SSE)."""
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"No session_id provided — generated session_id={session_id}")

    conversation_id = str(uuid.uuid4())
    logger.info(f"Stream request: query_len={len(body.query)} mode={body.stream_mode}")
    try:
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
        logger.error(f"Stream error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
