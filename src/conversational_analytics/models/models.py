from typing import Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


# ── LangGraph State ───────────────────────────────────────────────────

class AgentState(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]  # "messages" key required by ToolNode
    intermediate_steps: list[str]
    tool_results: list[str]
    final_response: str
    thinking: str
    tools_invoked: list[str]


# ── Request / Response ────────────────────────────────────────────────

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    query: str


class AgentMetadata(BaseModel):
    tools_invoked: list[str] = Field(default_factory=list)
    thinking: str | None = None


class AgentResponse(BaseModel):
    response_text: str
    metadata: AgentMetadata = Field(default_factory=AgentMetadata)
