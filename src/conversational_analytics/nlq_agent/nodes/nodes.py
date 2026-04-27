import asyncio
import json
import logging
import re
import time
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore
from conversational_analytics.models import AgentState
from conversational_analytics.nlq_agent.tools import get_sql_tools, get_system_message
from conversational_analytics.config import get_settings
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)


async def agent_node(state: AgentState, store: BaseStore) -> dict:
    """Calls the LLM with tools bound. Reads long-term memory from store."""
    cfg = get_settings()
    tools_invoked = state.get("tools_invoked", [])
    role = state.get("role")
    user_id = state.get("user_id") or ""
    conversation_id = state.get("conversation_id", "")

    logger.debug(f"agent_node called — user={user_id} role={role} conversation={conversation_id} step={len(tools_invoked)+1}")

    tools = get_sql_tools(role)
    system_msg = get_system_message(role)

    # ── Long-term recall: semantic search over past conversation summaries ──
    # Only on the first turn of a session (messages has exactly 1 entry — the new HumanMessage).
    # Subsequent turns already have Redis short-term context, so the embedding call is skipped.
    is_first_session_turn = len(state.get("messages", [])) <= 1
    memory_context = ""
    if cfg.long_term_memory_enabled and user_id and store and not tools_invoked and is_first_session_turn:
        logger.debug(f"First session turn — semantic search for user={user_id}")
        try:
            from conversational_analytics.memory import search_similar_conversations
            past = await asyncio.wait_for(
                search_similar_conversations(
                    user_id=user_id,
                    query=state.get("user_input", ""),
                    limit=cfg.memory_long_term_recall_limit,
                ),
                timeout=1.0,
            )
            if past:
                summaries = "\n".join(
                    f"- {r['summary']} (similarity: {r['similarity']:.2f})"
                    for r in past
                    if r.get("summary")
                )
                if summaries:
                    memory_context = f"\n\nRelevant past conversations (semantic search):\n{summaries}"
                    logger.info(f"Recalled {len(past)} semantically similar conversations for user={user_id}")
            else:
                logger.debug(f"No similar past conversations found for user={user_id}")
        except asyncio.TimeoutError:
            logger.warning(f"Semantic search timed out (>1s) for user={user_id} — proceeding without memory context")
        except Exception as e:
            logger.warning(f"Semantic search failed for user={user_id}: {e}")
    elif tools_invoked:
        logger.debug(f"ReAct loop — skipping memory recall (tools_invoked={tools_invoked})")
    elif not is_first_session_turn:
        logger.debug(f"Subsequent session turn — skipping long-term recall, Redis has context")

    enriched_system = SystemMessage(
        content=system_msg.content + memory_context
    ) if memory_context else system_msg

    prompt_text = enriched_system.content if cfg.log_prompt else None
    if cfg.log_prompt:
        logger.debug(f"Prompt captured ({len(enriched_system.content)} chars) for audit log")

    # guard: if max iterations reached, force the LLM to respond without tools
    if len(tools_invoked) >= cfg.agent_max_iterations:
        logger.warning(f"Max iterations ({cfg.agent_max_iterations}) reached for conversation={conversation_id} — forcing final response without tools")
        response: AIMessage = get_llm().invoke(
            [enriched_system]
            + state["messages"]
            + [HumanMessage(content="You have used the maximum number of tool calls. Based on what you have found so far, provide your final answer now. Do not call any more tools.")]
        )
    else:
        logger.debug(f"Invoking LLM with {len(tools)} tools bound (iteration {len(tools_invoked)+1})")
        messages = state["messages"]
        if cfg.memory_short_term_message_limit > 0 and len(messages) > cfg.memory_short_term_message_limit:
            messages = messages[-cfg.memory_short_term_message_limit:]
            logger.debug(f"Short-term history trimmed to last {cfg.memory_short_term_message_limit} messages (total={len(state['messages'])})")
        response: AIMessage = get_llm().bind_tools(tools).invoke(
            [enriched_system] + messages
        )

    thinking = response.additional_kwargs.get("thinking", "") if hasattr(response, "additional_kwargs") else ""

    if response.tool_calls:
        tool_names = [tc["name"] for tc in response.tool_calls]
        logger.info(f"LLM decided to call tools: {tool_names} (conversation={conversation_id})")
    else:
        logger.info(f"LLM generated final response ({len(str(response.content))} chars) for conversation={conversation_id}")

    step = f"Agent responded: {response.content[:100]}..." if response.content else "Agent invoked tools"

    # accumulate token usage across all LLM calls
    current_usage = state.get("token_usage") or {
        "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
        "reasoning_tokens": 0, "cache_read_tokens": 0,
    }
    if response.usage_metadata:
        um = response.usage_metadata
        current_usage["input_tokens"] += um.get("input_tokens", 0)
        current_usage["output_tokens"] += um.get("output_tokens", 0)
        current_usage["total_tokens"] += um.get("total_tokens", 0)
        current_usage["reasoning_tokens"] += um.get("output_token_details", {}).get("reasoning", 0)
        current_usage["cache_read_tokens"] += um.get("input_token_details", {}).get("cache_read", 0)
        logger.debug(f"Token usage this call — input={um.get('input_tokens',0)} output={um.get('output_tokens',0)} total={um.get('total_tokens',0)}")

    return {
        "messages": [response],
        "intermediate_steps": state.get("intermediate_steps", []) + [step],
        "thinking": thinking,
        "token_usage": current_usage,
        "prompt": prompt_text,
    }


def tools_node(state: AgentState) -> dict:
    """Runs ToolNode and tracks which tools were invoked and their results."""
    role = state.get("role")
    conversation_id = state.get("conversation_id", "")
    tools = get_sql_tools(role)

    logger.debug(f"tools_node called — conversation={conversation_id} role={role}")
    result = ToolNode(tools).invoke(state)

    tool_messages: list[ToolMessage] = [m for m in result.get("messages", []) if isinstance(m, ToolMessage)]
    tools_invoked = [m.name for m in tool_messages]
    tool_results = [m.content for m in tool_messages]

    for msg in tool_messages:
        logger.info(f"Tool executed: {msg.name} — result length: {len(msg.content)} chars (conversation={conversation_id})")
        logger.debug(f"Tool '{msg.name}' result preview: {msg.content[:200]}")

    return {
        "messages": tool_messages,
        "tool_results": state.get("tool_results", []) + tool_results,
        "tools_invoked": state.get("tools_invoked", []) + tools_invoked,
        "intermediate_steps": state.get("intermediate_steps", []) + [f"Tools called: {tools_invoked}"],
    }


def response_formatter_node(state: AgentState) -> dict:
    """Extracts the final text response and optional Vega spec."""
    conversation_id = state.get("conversation_id", "")
    logger.debug(f"response_formatter_node called — conversation={conversation_id}")

    for msg in reversed(state["messages"]):
        if not isinstance(msg, AIMessage) or not msg.content:
            continue
        extracted = _extract_text(msg.content)
        text, vega_spec = _extract_vega_spec(extracted)
        if text or vega_spec:
            logger.info(f"Final response extracted: {len(text)} chars, has_vega={vega_spec is not None} (conversation={conversation_id})")
            if vega_spec:
                logger.debug(f"Vega spec extracted: mark={vega_spec.get('mark')}, title={vega_spec.get('title')}")
            return {"final_response": text, "vega_spec": vega_spec}

    logger.warning(f"No final response found in messages for conversation={conversation_id}")
    return {"final_response": "I could not generate a response.", "vega_spec": None}


def _extract_vega_spec(text: str) -> tuple[str, dict | None]:
    """Extracts a vega code block from the response text."""
    pattern = r"```vega\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if not match:
        return text, None
    try:
        parsed = json.loads(match.group(1).strip())
        if isinstance(parsed, dict) and "vega_spec" in parsed and len(parsed) == 1:
            logger.debug("Unwrapping nested vega_spec key from LLM response")
            parsed = parsed["vega_spec"]
        if not isinstance(parsed, dict) or not _is_valid_vega_spec(parsed):
            logger.warning("Parsed vega block does not look like a valid Vega-Lite spec")
            return text, None
        clean_text = re.sub(pattern, "", text).strip()
        return clean_text, parsed
    except json.JSONDecodeError as e:
        logger.warning(f"Found vega block but failed to parse as JSON: {e}")
        return text, None


def _is_valid_vega_spec(spec: dict) -> bool:
    """Validates a Vega-Lite spec — handles all top-level composite structures."""
    # simple mark at top level
    if "mark" in spec:
        return True
    # layered chart: layer[0] has mark
    if "layer" in spec and isinstance(spec["layer"], list) and spec["layer"]:
        return True
    # faceted / repeated chart: spec key contains the mark
    if "spec" in spec and isinstance(spec["spec"], dict):
        return True
    # horizontal / vertical concat
    if "hconcat" in spec or "vconcat" in spec or "concat" in spec:
        return True
    return False


def _extract_text(content) -> str:
    """Handles both plain string and list-of-parts content (Gemini thinking models)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part["text"] for part in content
            if isinstance(part, dict) and part.get("type") == "text" and part.get("text")
        )
    return str(content) if content else ""
