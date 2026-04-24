import uuid
from typing import Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


# ── LangGraph State ───────────────────────────────────────────────────

class AgentState(TypedDict):
    user_input: str
    user_id: str | None
    conversation_id: str
    messages: Annotated[list, add_messages]
    intermediate_steps: list[str]
    tool_results: list[str]
    final_response: str
    vega_spec: dict | None
    thinking: str
    tools_invoked: list[str]
    role: str | None
    token_usage: dict | None
    prompt: str | None  # system prompt captured on first agent call (LOG_PROMPT=true)


# ── Request / Response ────────────────────────────────────────────────

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    query: str
    role: str | None = None
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AgentMetadata(BaseModel):
    conversation_id: str | None = None
    tools_invoked: list[str] = Field(default_factory=list)
    thinking: str | None = None
    token_usage: dict | None = None


class AgentResponse(BaseModel):
    response_text: str
    vega_spec: dict | None = None
    metadata: AgentMetadata = Field(default_factory=AgentMetadata)
