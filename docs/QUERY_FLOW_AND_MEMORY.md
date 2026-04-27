# Query Flow & Memory Architecture

## 1. End-to-End Query Flow

```
HTTP POST /api/v1/chat  or  /api/v1/stream
         │
         ▼
  nlq_controller.py
  ├── Validate & sanitize input (nh3)
  ├── Generate conversation_id (uuid4)
  ├── session_id from X-Session-Id header (or generate new)
  ├── Return X-Session-Id in response header
  └── Call run_agent(request)  or  stream_agent(request)
         │
         ▼
  agent_service.py  →  _graph.astream()
         │
         ├── Per node chunk: _process_chunk()
         │     ├── agent node   → _fire_log_agent_step() [enqueue, ~1µs]
         │     └── tools node   → _fire_log_agent_step() [enqueue, ~1µs]
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │             LangGraph StateGraph             │
  │                                              │
  │  agent_node ──► tools_node ──► agent_node   │
  │      │               (ReAct loop)            │
  │      └─────────────────────► response_       │
  │                              formatter_node  │
  └──────────────────────────────────────────────┘
         │
         ├──► HTTP response / SSE "done" returned to client immediately
         │
         └──► asyncio.create_task(_persist_audit())   [background, non-blocking]
                   ├── audit_writer.enqueue_query_log()     [always, ~1µs]
                   └── save_conversation_summary()          [only if LONG_TERM_MEMORY_ENABLED=true]
```

---

## 2. /chat vs /stream — Flow Difference

Both endpoints use the same underlying `_graph.astream()` execution and `_process_chunk()` state tracking. The difference is only in how chunks are delivered to the client:

| | `/chat` (`run_agent`) | `/stream` (`stream_agent`) |
|---|---|---|
| Graph execution | Identical | Identical |
| Chunk handling | Buffers all chunks silently | Yields each chunk as SSE event immediately |
| Client receives | One JSON response when graph finishes | Progressive SSE events as graph executes |
| `_persist_audit` | `create_task` after graph finishes | `create_task` after `done` SSE event is yielded |
| Response header | `X-Session-Id` | `X-Session-Id` |

---

## 3. Short-Term Memory

**Backend:** Configurable via `SHORT_TERM_MEMORY_TYPE` — `redis` (default, production) or `inmemory` (local dev only).

**Implementation:** `AsyncRedisSaver` (Redis) or `MemorySaver` (in-memory), used as LangGraph checkpointer.

**What it stores:** Full `AgentState` per session — all `HumanMessage`, `AIMessage`, `ToolMessage` objects, intermediate steps, token usage, tool results.

**Key:** `thread_id = session_id` passed via `config = {"configurable": {"thread_id": request.session_id}}`.

**When it's READ:**
LangGraph reads it automatically at the start of every `_graph.astream()` call. Before `agent_node` runs, the checkpointer loads the previous state for that `thread_id` and merges it with the new input — giving the LLM full conversation history across all turns of the same session.

**When it's WRITTEN:**
LangGraph writes automatically after every node completes (`agent_node`, `tools_node`, `response_formatter_node`). Each node's state delta is checkpointed incrementally.

**Message window limit:**
Controlled by `MEMORY_SHORT_TERM_MESSAGE_LIMIT` (default `0` = unlimited). When set, only the last N messages are sent to the LLM — reduces token usage for long sessions but risks losing earlier context.

**Latency impact:**
- Read: ~1–3ms. Happens once before graph starts — on the critical path but negligible.
- Write: ~1–2ms per node. On the critical path but negligible.

**Scope:** Per-session only. New `session_id` = no history. Data expires per Redis TTL (`SHORT_TERM_MEMORY_SESSION_TTL`, default 3600s).

---

## 4. Long-Term Memory

**Controlled by:** `LONG_TERM_MEMORY_ENABLED` (default `true`). When `false`, both read and write are skipped entirely — no Vertex AI embedding calls, no pgvector queries.

**Backend:** `AsyncPostgresStore` (LangGraph) with `AsyncConnectionPool` (psycopg async). Embeddings stored in `store_vectors` table via pgvector. Document stored in `public.store`.

**What it stores:** Compressed conversation summaries. Format: `"Q: <first 150 chars> | A: <first 300 chars>"`. Auto-embedded on write via `GoogleGenerativeAIEmbeddings` (Vertex AI, `text-embedding-005`, 768 dims).

**Key:** namespace = `("conversation_summaries", user_id)`, key = `conversation_id`.

**When it's READ:**
Inside `agent_node`, guarded by three conditions:

```python
if cfg.long_term_memory_enabled and user_id and store and not tools_invoked and is_first_session_turn:
    past = await asyncio.wait_for(
        search_similar_conversations(user_id, query, limit=cfg.memory_long_term_recall_limit),
        timeout=1.0,
    )
```

- `long_term_memory_enabled` — feature flag, skips entirely if false
- `not tools_invoked` — skips on every ReAct loop iteration after the first LLM call
- `is_first_session_turn` (`len(messages) <= 1`) — skips on follow-up turns within the same session; Redis already has full context for those
- `timeout=1.0` — if Vertex AI or pgvector is slow, proceeds without memory context rather than stalling

Top N results (configured via `MEMORY_LONG_TERM_RECALL_LIMIT`, default `3`) are injected into the system prompt as `"Relevant past conversations"`.

**When it's WRITTEN:**
In `_persist_audit()`, fired as `asyncio.create_task` after graph completes. `save_conversation_summary()` calls `store.aput()` which auto-generates the embedding and writes to both `public.store` and `store_vectors`.

**Latency impact:**
- Read: 50–200ms, capped at 1s timeout. Only on first turn of a new session — on the critical path for that turn only.
- Write: 100–300ms. Runs in background task — completely off the critical path.

**Scope:** Cross-session, per-user. Persists indefinitely. Enables the LLM to recall context from previous sessions.

---

## 5. Audit Logging

**Backend:** `AuditWriter` — production-grade async queue-based writer (`audit_writer.py`).

**Tables:** `memory.query_log` (one row per conversation) and `memory.agent_steps` (one row per ReAct step).

**Always runs regardless of `LONG_TERM_MEMORY_ENABLED`.** Audit logs are operational records, not memory.

**Architecture:**

```
enqueue_query_log() / enqueue_agent_step()
         │  ~1µs, put_nowait, never blocks event loop
         ▼
  asyncio.Queue (bounded, max 10,000 items)
         │
         ▼
  Background worker (_worker coroutine)
  ├── Collects up to 50 items per batch (or flushes after 0.5s)
  ├── Splits batch into query_logs + agent_steps
  ├── Writes via cursor.executemany() — single round-trip per type
  ├── Exponential backoff retry (3 attempts: 0.5s → 1s → 2s)
  └── Drops batch with ERROR log after 3 failures
```

**When it's WRITTEN:**
- `enqueue_agent_step()` — called via `_fire_log_agent_step()` inside `_process_chunk()` during graph streaming. One call per `agent` node output (LLM call) and one per `tools` node output (tool result). Returns in ~1µs.
- `enqueue_query_log()` — called inside `_persist_audit()` background task after graph completes. Returns in ~1µs.

**Graceful shutdown:** `audit_writer.stop()` in lifespan calls `queue.join()` with a 30s timeout — drains all queued items before closing the DB pool.

**Backpressure:** If the queue reaches 10,000 items (e.g. DB is down for an extended period), new items are dropped with a WARNING log. This protects the event loop from unbounded memory growth.

**Latency impact:** ~1µs on the event loop for both enqueue calls. The actual DB write happens in the background worker — zero impact on request latency.

---

## 6. Persist Flow

```
graph completes
     │
     ├──► HTTP response / SSE "done" returned to client immediately
     │
     └──► asyncio.create_task(_persist_audit())   [background]
               │
               ├── audit_writer.enqueue_query_log()    [~1µs, always]
               │         └──► queue → worker → DB batch insert
               │
               └── if LONG_TERM_MEMORY_ENABLED:
                       save_conversation_summary()     [async, Vertex AI + pgvector]
```

**Trade-off:** If the server process crashes between response and task completion, that conversation's audit record and summary may be lost. Acceptable for analytics audit logs — the `queue.join()` drain on graceful shutdown mitigates this for planned restarts.

---

## 7. Configuration Reference

| Key | Default | Controls |
|---|---|---|
| `SHORT_TERM_MEMORY_TYPE` | `redis` | `redis` or `inmemory` backend |
| `SHORT_TERM_MEMORY_HOST` | `localhost` | Redis host |
| `SHORT_TERM_MEMORY_PORT` | `6379` | Redis port |
| `SHORT_TERM_MEMORY_PASSWORD` | `` | Redis password (optional) |
| `SHORT_TERM_MEMORY_SESSION_TTL` | `3600` | Redis key TTL in seconds |
| `MEMORY_SHORT_TERM_MESSAGE_LIMIT` | `0` | Max messages sent to LLM (0 = unlimited) |
| `LONG_TERM_MEMORY_ENABLED` | `true` | Enable/disable pgvector read + write |
| `MEMORY_LONG_TERM_RECALL_LIMIT` | `3` | Max past summaries injected into prompt |
| `EMBEDDING_MODEL` | `text-embedding-005` | Vertex AI embedding model |
| `EMBEDDING_DIMENSION` | `768` | Embedding vector dimensions |

---

## 8. Summary Table

| Layer | Technology | Read timing | Write timing | On critical path | Latency |
|---|---|---|---|---|---|
| Short-term | Redis `AsyncRedisSaver` or `MemorySaver` | Before graph starts (auto) | After each node (auto) | Yes | ~1–5ms |
| Long-term recall | `AsyncPostgresStore` + pgvector | First turn of new session only (if enabled) | Background task (if enabled) | Read only, capped 1s | Read: 50–200ms, Write: off-path |
| Audit steps | `AuditWriter` async queue | Never | During graph streaming (~1µs enqueue) | No | ~1µs |
| Audit query log | `AuditWriter` async queue | Never | Background task (~1µs enqueue) | No | ~1µs |
