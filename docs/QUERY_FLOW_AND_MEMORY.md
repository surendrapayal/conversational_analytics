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
  _persist_audit()   ← called AFTER graph completes
  ├── log_query()         → memory.query_log (PostgreSQL, sync)
  └── save_conversation_summary() → AsyncPostgresStore + pgvector (async)
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
Inside `agent_node`, on the **first LangGraph iteration only** (when `tools_invoked` is empty). It calls `search_similar_conversations()` which does a pgvector cosine similarity search against the user's past summaries. The top 3 results are injected into the system prompt as context before the LLM is called.

```python
# nodes.py — only on first agent call
if user_id and store and not tools_invoked:
    past = await search_similar_conversations(user_id, query, limit=3)
    # → appended to system prompt as "Relevant past conversations"
```

**When it's WRITTEN:**
In `_persist_audit()`, called **after the graph fully completes**. `save_conversation_summary()` calls `store.aput()` which auto-generates the embedding via `GoogleGenerativeAIEmbeddings` and stores both the document and vector.

**Latency impact:**
- Read (`asearch`): **50–200ms** — this is on the critical path. It involves an embedding API call to Vertex AI (to embed the query) + a pgvector ANN search. This adds latency to every first LLM call.
- Write (`aput`): **100–300ms** — embedding generation + PostgreSQL insert. This is called in `_persist_audit()` which is `await`ed **sequentially after** the graph completes, so it adds latency to the total response time before the HTTP response is returned.

**Scope:** Cross-session, per-user. Persists indefinitely. Enables the LLM to recall what a user asked about in previous sessions.

---

## 4. Audit Log (PostgreSQL — psycopg2 sync)

**Tables:** `memory.query_log` and `memory.agent_steps`

**What it stores:**
- `memory.query_log`: One row per conversation — query, SQL generated, response, vega spec, token usage, all SSE stream events (JSONB), execution time.
- `memory.agent_steps`: One row per ReAct step — tool name, input/output, token usage per step, duration.

**When it's WRITTEN:**
- `log_agent_step()` — called inside `_process_chunk()` during graph streaming, once per `agent` node output and once per `tools` node output. Uses a `psycopg2.ThreadedConnectionPool`.
- `log_query()` — called in `_persist_audit()` after graph completes.

**Latency impact:** `log_agent_step()` is sync and called inline during streaming — it uses a thread pool connection but **does block** briefly (~2–5ms per step). `log_query()` is also sync and sequential in `_persist_audit()`.

---

## 5. Sequential vs Fire-and-Forget

This is the most important thing to understand about the current design:

```
_persist_audit() is awaited sequentially:

  graph completes
       │
       ▼
  log_query()                  ← sync, ~5–10ms
       │
       ▼
  save_conversation_summary()  ← async, ~100–300ms (embedding + DB write)
       │
       ▼
  HTTP response returned
```

**Both writes are sequential and on the critical path.** The user waits for both before getting a response. `save_conversation_summary()` is the expensive one — it calls the Vertex AI embedding API synchronously in the await chain.

**For `/stream`**, the `done` SSE event is sent to the client before `_persist_audit()` is called, so the user sees the response immediately. But the server-side generator is still running until persist completes — the HTTP connection stays open.

**If you want true fire-and-forget** to eliminate that latency, `_persist_audit` could be wrapped in `asyncio.create_task()`:

```python
# agent_service.py — fire-and-forget pattern (not current code)
asyncio.create_task(_persist_audit(request, state, execution_ms))
```

The trade-off: if the server crashes before the task runs, the audit record is lost.

---

## 6. Summary Table

| Memory Layer | Technology | Read timing | Write timing | On critical path | Typical latency |
|---|---|---|---|---|---|
| Short-term | Redis `AsyncRedisSaver` | Before graph starts (auto) | After each node (auto) | Yes (read + write) | 1–5ms |
| Long-term recall | `AsyncPostgresStore` + pgvector | First `agent_node` call only | After graph completes | Yes (read) | Read: 50–200ms, Write: 100–300ms |
| Audit log (steps) | psycopg2 sync | Never | During graph streaming | Yes | 2–5ms per step |
| Audit log (query) | psycopg2 sync | Never | After graph completes | Yes | 5–10ms |
