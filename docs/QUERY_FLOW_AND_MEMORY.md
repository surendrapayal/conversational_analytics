# Query Flow & Memory Architecture

## 1. End-to-End Query Flow

```
HTTP POST /api/v1/chat  or  /api/v1/stream
         │
         ▼
  nlq_controller.py
  ├── Validate & sanitize input (nh3)
  ├── Generate conversation_id (uuid4)
  ├── session_id from header (or generate new)
  └── Call run_agent(request)  or  stream_agent(request)
         │
         ▼
  agent_service.py  →  _graph.astream()
         │
         ▼
  ┌──────────────────────────────────────────┐
  │           LangGraph StateGraph           │
  │                                          │
  │  agent_node ──► tools_node ──► agent_node│
  │      │              (loop)               │
  │      └──────────────────► response_      │
  │                           formatter_node │
  └──────────────────────────────────────────┘
         │
         ▼
  asyncio.create_task(_persist_audit())   ← fire-and-forget, does NOT block response
  ├── log_query()              → run_in_executor (thread pool) ─┐ asyncio.gather
  └── save_conversation_summary() → AsyncPostgresStore + pgvector ┘ (concurrent)
```

---

## 2. Short-Term Memory (Redis — `AsyncRedisSaver`)

**What it stores:** The full LangGraph `AgentState` — all messages in the conversation thread (HumanMessage, AIMessage, ToolMessage), intermediate steps, token usage, tool results.

**Key:** `thread_id = session_id` (passed via `config = {"configurable": {"thread_id": request.session_id}}`)

**When it's READ:**
LangGraph reads it automatically at the start of every `_graph.astream()` call. Before `agent_node` even runs, LangGraph's checkpointer loads the previous state for that `thread_id` from Redis and merges it with the new input. This gives the LLM the full conversation history across multiple turns within the same session.

**When it's WRITTEN:**
LangGraph writes to Redis automatically after every node completes — `agent_node`, `tools_node`, `response_formatter_node`. Each node's state delta is checkpointed incrementally.

**Latency impact:**
- Read: ~1–3ms (local Redis). Happens once before the graph starts — **on the critical path**.
- Write: ~1–2ms per node, 3–4 writes per query. Happens inside the graph execution — **on the critical path** but negligible.
- Redis is in-process async so it does not block the event loop.

**Scope:** Per-session only. If the user starts a new session (new `session_id`), Redis has no history. Data expires based on Redis TTL config.

---

## 3. Long-Term Memory (PostgreSQL — `AsyncPostgresStore` + pgvector)

**What it stores:** Compressed conversation summaries with vector embeddings. Format: `"Q: <first 150 chars of query> | A: <first 300 chars of response>"`. Stored in `public.store` table, embeddings in `store_vectors` table (managed by LangGraph).

**Key:** namespace = `("conversation_summaries", user_id)`, key = `conversation_id`

**When it's READ:**
Inside `agent_node`, on the **first turn of a session only** — guarded by two conditions:

```python
# nodes.py
is_first_session_turn = len(state.get("messages", [])) <= 1
if user_id and store and not tools_invoked and is_first_session_turn:
    past = await asyncio.wait_for(
        search_similar_conversations(user_id, query, limit=3),
        timeout=1.0,
    )
    # → top 3 results appended to system prompt as "Relevant past conversations"
```

- `not tools_invoked` — skips recall on every ReAct loop iteration after the first.
- `is_first_session_turn` — skips recall on follow-up messages within the same session. Redis already holds the full conversation history for those turns, so the Vertex AI embedding call is unnecessary.
- `timeout=1.0` — if pgvector or Vertex AI is slow, the LLM call proceeds after 1 second without memory context rather than stalling the user.

**When it's WRITTEN:**
In `_persist_audit()`, fired as a background task after the graph completes. `save_conversation_summary()` calls `store.aput()` which auto-generates the embedding via `GoogleGenerativeAIEmbeddings` and stores both the document and vector.

**Latency impact (after optimizations):**
- Read (`asearch`): **50–200ms**, capped at **1s timeout**. Only on the first message of a new session — **on the critical path** for that turn only.
- Write (`aput`): **100–300ms** — now runs as a background `asyncio.create_task`, completely off the critical path.

**Scope:** Cross-session, per-user. Persists indefinitely. Enables the LLM to recall what a user asked about in previous sessions.

---

## 4. Audit Log (PostgreSQL — `ThreadPoolExecutor`)

**Tables:** `memory.query_log` and `memory.agent_steps`

**What it stores:**
- `memory.query_log`: One row per conversation — query, SQL generated, response, vega spec, token usage, all SSE stream events (JSONB), execution time.
- `memory.agent_steps`: One row per ReAct step — tool name, input/output, token usage per step, duration.

**When it's WRITTEN:**
- `log_agent_step()` — called via `_fire_log_agent_step()` inside `_process_chunk()` during graph streaming. Submitted to a dedicated `ThreadPoolExecutor(max_workers=4)` using `executor.submit()` — completely non-blocking, no `await` required.
- `log_query()` — called inside `_persist_audit()` via `loop.run_in_executor()`, running concurrently with `save_conversation_summary()` via `asyncio.gather`.

**Latency impact (after optimizations):**
- `log_agent_step()`: **0ms on event loop** — offloaded to thread pool, fire-and-forget.
- `log_query()`: **0ms on event loop** — runs in thread pool concurrently with the embedding write, both off the critical path via `create_task`.

---

## 5. Persist Flow — Before vs After Optimizations

**Before:**
```
graph completes
     │
     ▼ (await — blocks response)
log_query()                   ← sync psycopg2, ~5–10ms, blocks event loop
     │
     ▼ (await — blocks response)
save_conversation_summary()   ← Vertex AI embed + DB write, ~100–300ms
     │
     ▼
HTTP response returned         ← user waits ~110–310ms after graph finishes
```

**After:**
```
graph completes
     │
     ├──► HTTP response returned immediately  ← user gets response here
     │
     └──► asyncio.create_task(_persist_audit())   ← background, non-blocking
               │
               └──► asyncio.gather(
                        run_in_executor(log_query),        ─┐ concurrent
                        save_conversation_summary(),        ┘
                    )
```

The user receives the response as soon as the graph finishes. Audit persistence happens entirely in the background. Total background time = `max(log_query, save_summary)` instead of `log_query + save_summary`.

**Trade-off:** If the server process crashes in the milliseconds between response and task completion, that conversation's audit record is lost. This is acceptable for an analytics audit log.

---

## 6. Summary Table

| Memory Layer | Technology | Read timing | Write timing | On critical path | Typical latency |
|---|---|---|---|---|---|
| Short-term | Redis `AsyncRedisSaver` | Before graph starts (auto) | After each node (auto) | Yes (read + write) | 1–5ms |
| Long-term recall | `AsyncPostgresStore` + pgvector | First turn of new session only | Background task | Read only, capped 1s | Read: 50–200ms (max 1s), Write: off-path |
| Audit log (steps) | `ThreadPoolExecutor` | Never | During graph streaming (thread pool) | No | ~0ms on event loop |
| Audit log (query) | `ThreadPoolExecutor` | Never | Background task (concurrent with summary) | No | ~0ms on event loop |
