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


# def sanitize_input(value: str) -> str:
#     """Strips all HTML tags and attributes using nh3 to prevent XSS.

#     Returns the sanitized plain-text string.
#     Raises ValueError if the value is empty after sanitization.
#     """
#     sanitized = nh3.clean(value, tags=set())  # strip ALL tags — plain text only
#     sanitized = sanitized.strip()
#     if not sanitized:
#         raise ValueError("Input is empty or contains only HTML/script content")
#     return sanitized

def sanitize_input(value: str, field_name: str) -> str:
    
    """
    Validates and sanitizes a user-provided string by removing all HTML tags
    and ensuring the original input does not contain any disallowed content.

    This function uses nh3 to strip all HTML tags and attributes, enforcing
    plain-text input. If the sanitized value differs from the original input,
    it indicates the presence of HTML or potentially unsafe content (e.g., scripts),
    and the function raises a ValueError instead of silently modifying the input.

    Args:
        value (str): The raw input string provided by the user.
        field_name (str): The name of the field being validated, used for
                          meaningful error messages.

    Returns:
        str: The sanitized plain-text string (unchanged from input if valid).

    Raises:
        ValueError: If the input contains HTML tags, script content, or any
                    characters removed during sanitization.

    Notes:
        - This function follows a strict "validate and reject" approach rather
          than silently sanitizing input.
        - Suitable for structured inputs such as form fields, API parameters,
          and system commands where only plain text is expected.
    """
    
    sanitized = nh3.clean(value, tags=set())
    sanitized = sanitized.strip()

    if value != sanitized:
        raise ValueError(
            f"Invalid characters detected in '{field_name}': HTML/script not allowed."
        )

    return sanitized

class QueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=QUERY_MIN_LENGTH, max_length=QUERY_MAX_LENGTH,
                       description=f"Natural language query ({QUERY_MIN_LENGTH}-{QUERY_MAX_LENGTH} characters)")
    stream_mode: Literal["standard", "verbose"] = Field(
        default="standard",
        description="standard = business-friendly output | verbose = full internal details"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Sanitize query for XSS and validate length after sanitization."""
        sanitized = sanitize_input(v, "query")
        if len(sanitized) < QUERY_MIN_LENGTH:
            raise ValueError(f"Query must be at least {QUERY_MIN_LENGTH} characters after sanitization")
        if len(sanitized) > QUERY_MAX_LENGTH:
            raise ValueError(f"Query must not exceed {QUERY_MAX_LENGTH} characters")
        logger.debug(f"Query sanitized: original_len={len(v)} sanitized_len={len(sanitized)}")
        return sanitized

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Sanitize user_id for XSS."""
        return sanitize_input(v, "user_id")


@router.post("/chat", response_model=AgentResponse)
def query(
    body: QueryRequest,
    session_id: str = Header(None, description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role: admin | general_manager | location_manager | staff"),
):
    """Accepts a natural language query and returns a SQL-backed response."""
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"No session_id provided — generated session_id={session_id}")

    conversation_id = str(uuid.uuid4())
    logger.info(f"Chat request: user_id={body.user_id} session={session_id} role={role} conversation={conversation_id}")
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
    session_id: str = Header(None, description="Session ID for conversation memory"),
    role: str | None = Header(None, description="User role: admin | general_manager | location_manager | staff"),
):
    """Streams agent execution as Server-Sent Events (SSE).
    Events: thinking | tool_call | tool_result | response | done
    """
    try:
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.debug(f"No session_id provided — generated session_id={session_id}")

        conversation_id = str(uuid.uuid4())
        logger.info(f"Stream request: user_id={body.user_id} session={session_id} role={role} conversation={conversation_id} mode={body.stream_mode}")
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
