# Memory Architecture

## Overview

The system uses a **three-tier memory architecture** to give the agent both within-session continuity and cross-session learning:

| Tier | Storage | Scope | Persistence |
|---|---|---|---|
| Short-term (checkpoint) | Redis | Within a session | TTL-based (default 1 hour) |
| Long-term (store) | PostgreSQL + pgvector | Across all sessions per user | Permanent |
| Audit log | PostgreSQL | All conversations | Permanent |

---

## Tier 1 — Short-Term Memory (Redis Checkpointer)

### Purpose
Maintains the full LangGraph state (message history, intermediate steps, tool results) across multiple turns **within the same session**. This is what allows the user to ask follow-up questions like "now show me just the top 3" and have the agent understand the context.

### Implementation
- **Class**: `AsyncRedisSaver` from `langgraph-checkpoint-redis`
- **Fallback**: `MemorySaver` (in-process, non-persistent) when `SHORT_TERM_MEMORY_TYPE=inmemory`
- **Key**: LangGraph uses `thread_id = session_id` as the checkpoint key in Redis.
- **TTL**: Configurable via `SHORT_TERM_MEMORY_SESSION_TTL` (default: 3600 seconds).

### Configuration
```
SHORT_TERM_MEMORY_TYPE=redis          # redis | inmemory
SHORT_TERM_MEMORY_HOST=localhost
SHORT_TERM_MEMORY_PORT=6379
SHORT_TERM_MEMORY_PASSWORD=           # optional
SHORT_TERM_MEMORY_SESSION_TTL=3600
```

### What is stored in Redis
LangGraph serialises the entire `AgentState` TypedDict as a checkpoint:
- `messages` — full conversation history (HumanMessage, AIMessage, ToolMessage)
- `intermediate_steps` — list of step descriptions
- `tool_results` — raw tool outputs
- `tools_invoked` — list of tool names called
- `final_response`, `vega_spec`, `thinking`, `token_usage`

### Message history trimming
When `MEMORY_SHORT_TERM_MESSAGE_LIMIT > 0`, the agent node trims the message list to the last N messages before sending to the LLM. This prevents the context window from growing unbounded in long sessions. Set to `0` (default) for unlimited history.

### Flow
```
Turn 1:  User asks Q1
         → graph runs with thread_id=session_id
         → LangGraph saves checkpoint to Redis key: session_id

Turn 2:  User asks Q2 (follow-up)
         → graph loads checkpoint from Redis
         → messages = [Q1, A1, Q2]  ← full history restored
         → agent has full context of Q1/A1
```

---

## Tier 2 — Long-Term Memory (PostgreSQL + pgvector)

### Purpose
Enables the agent to recall **semantically similar past conversations** from previous sessions. When a user asks a new question, the system searches their conversation history for similar past Q&A pairs and injects the most relevant summaries into the system prompt. This allows the agent to learn user preferences and avoid repeating mistakes.

### Implementation
- **Class**: `AsyncPostgresStore` from `langgraph-postgres`
- **Embedding model**: Google `text-embedding-005` (768 dimensions, Vertex AI)
- **Vector index**: HNSW index on `store_vectors.embedding` using cosine similarity
- **Namespace**: `("conversation_summaries", user_id)` — each user has their own namespace
- **Key**: `conversation_id` (UUID)

### Database Tables

#### `store` — Document store
```sql
CREATE TABLE store (
    prefix      TEXT        NOT NULL,   -- namespace: "conversation_summaries\x1fuser_id"
    key         TEXT        NOT NULL,   -- conversation_id
    value       JSONB       NOT NULL,   -- {summary, session_id, conversation_id, role}
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    ttl_minutes DOUBLE PRECISION,
    PRIMARY KEY (prefix, key)
);
```

#### `store_vectors` — Embedding vectors
```sql
CREATE TABLE store_vectors (
    prefix      TEXT        NOT NULL,
    key         TEXT        NOT NULL,
    field_name  TEXT        NOT NULL,   -- always "summary"
    embedding   vector(768),            -- pgvector 768-dim embedding
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (prefix, key, field_name)
);

CREATE INDEX idx_store_vectors_embedding
    ON store_vectors USING hnsw (embedding vector_cosine_ops);
```

### What is stored
After every conversation, a summary is saved:
```
summary = "Q: {first 150 chars of user query} | A: {first 300 chars of agent response}"
```

The `AsyncPostgresStore` automatically generates the 768-dimensional embedding for the `summary` field and stores it in `store_vectors`.

### Semantic Search at Query Time
On the **first agent invocation** of each request (identified by `tools_invoked` being empty):

1. `search_similar_conversations(user_id, query, limit=3)` is called.
2. The query text is embedded using the same `text-embedding-005` model.
3. A cosine similarity search is performed against the user's stored embeddings.
4. The top-N results (default: 3, configurable via `MEMORY_LONG_TERM_RECALL_LIMIT`) are returned.
5. Summaries are formatted and appended to the system prompt:

```
Relevant past conversations (semantic search):
- Q: What is the net sales per location? | A: Here are the net sales... (similarity: 0.92)
- Q: Show revenue by location last month | A: The revenue breakdown... (similarity: 0.87)
```

The semantic search has a **30-second timeout** — if it times out or fails, the agent proceeds without memory context (graceful degradation).

### Semantic search is skipped on ReAct loop iterations
The search only runs on the first agent call per request. Subsequent agent calls (after tool results are returned) skip the search to avoid redundant embedding calls and latency.

### Configuration
```
LONG_TERM_MEMORY_ENABLED=true
MEMORY_SEMANTIC_SEARCH_ENABLED=true
MEMORY_LONG_TERM_RECALL_LIMIT=3       # number of past conversations to recall
EMBEDDING_MODEL=text-embedding-005
EMBEDDING_DIMENSION=768

LONG_TERM_MEMORY_DB_HOST=localhost
LONG_TERM_MEMORY_DB_PORT=5433
LONG_TERM_MEMORY_DB_NAME=zenvyra
LONG_TERM_MEMORY_DB_USER=admin_user
LONG_TERM_MEMORY_DB_PASSWORD=admin_password
```

### Connection pool
The `AsyncPostgresStore` uses an `AsyncConnectionPool` (psycopg-pool) with:
- `min_size=1`, `max_size=10`
- `autocommit=True`, `prepare_threshold=0`
- Singleton pattern with an `asyncio.Lock` to prevent race conditions during initialisation.

---

## Tier 3 — Audit Log (PostgreSQL)

### Purpose
A complete, immutable audit trail of every conversation and every agent step. Used for:
- The History page (session list + conversation detail)
- Debugging and observability
- Token usage tracking
- SQL query inspection

### Implementation
- **Class**: `AuditWriter` — a singleton async background writer
- **Pattern**: Producer-consumer with a bounded `asyncio.Queue` (max 10,000 items)
- **Worker**: Single background coroutine that drains the queue in batches of up to 50 rows
- **Batch timeout**: 0.5 seconds — flushes partial batches after this interval
- **Retry**: Exponential backoff, up to 3 attempts (0.5s → 1s → 2s)
- **Backpressure**: `put_nowait()` drops events with a warning if the queue is full (audit logs are non-critical — they must not block the main request path)
- **Graceful shutdown**: `stop()` waits up to 30 seconds for the queue to drain before closing the pool

### Database Tables

#### `query_log` — One row per conversation
```sql
CREATE TABLE query_log (
    id              BIGSERIAL   PRIMARY KEY,
    conversation_id UUID        NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    role            TEXT,
    user_query      TEXT        NOT NULL,
    prompt          TEXT,                   -- system prompt (if LOG_PROMPT=true)
    sql_generated   TEXT,                   -- last SQL query executed
    tools_invoked   TEXT[],                 -- array of tool names called
    agent_response  TEXT,
    vega_spec       JSONB,
    token_usage     JSONB,                  -- {input_tokens, output_tokens, total_tokens, ...}
    stream_events   JSONB,                  -- full SSE event log
    has_vega        BOOLEAN     NOT NULL DEFAULT FALSE,
    execution_ms    INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `agent_steps` — One row per ReAct step
```sql
CREATE TABLE agent_steps (
    id              BIGSERIAL   PRIMARY KEY,
    conversation_id UUID        NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    step_number     INT         NOT NULL,
    step_type       TEXT        NOT NULL,   -- "llm_call" | "tool_result"
    tool_name       TEXT,                   -- e.g. "sql_db_query"
    input           TEXT,
    output          TEXT,
    token_usage     JSONB,
    duration_ms     INT,
    prompt          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Write path (fire-and-forget)
```
stream_agent() completes
    │
    └─ asyncio.create_task(_persist_audit(...))   ← non-blocking, returns immediately
              │
              ├─ audit_writer.enqueue_query_log(...)   ← put_nowait() on queue
              └─ save_conversation_summary(...)        ← async, awaited inside task
                        │
                        └─ AsyncPostgresStore.aput(...)  ← saves summary + triggers embedding
```

The `AuditWriter` background worker:
```
Queue ──→ _collect_batch() ──→ _flush_with_retry()
              (up to 50 items,        │
               0.5s timeout)          ├─ _insert_query_logs()   (executemany)
                                      └─ _insert_agent_steps()  (executemany)
```

---

## Memory Lifecycle Diagram

```
User sends query
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent_node (first invocation)                                  │
│                                                                 │
│  1. Load session checkpoint from Redis (short-term memory)      │
│     → restores full message history for this session            │
│                                                                 │
│  2. Semantic search in PostgreSQL/pgvector (long-term memory)   │
│     → embed current query with text-embedding-005               │
│     → cosine similarity search over user's past summaries       │
│     → inject top-3 similar past Q&A into system prompt          │
│                                                                 │
│  3. Call LLM with enriched system prompt + message history      │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼  (ReAct loop: tool calls → tool results → agent → ...)
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  After final response                                           │
│                                                                 │
│  4. LangGraph saves updated checkpoint to Redis                 │
│     → new messages appended to session history                  │
│                                                                 │
│  5. asyncio.create_task(_persist_audit)                         │
│     ├─ enqueue_query_log → AuditWriter → query_log table        │
│     └─ save_conversation_summary                                │
│          → AsyncPostgresStore.aput()                            │
│          → auto-generates embedding for summary field           │
│          → stores in store + store_vectors tables               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Disabling Memory Components

All memory components can be independently disabled:

| Setting | Effect |
|---|---|
| `LONG_TERM_MEMORY_ENABLED=false` | Disables audit logging AND conversation summary saving |
| `MEMORY_SEMANTIC_SEARCH_ENABLED=false` | Disables semantic recall at query time (summaries still saved) |
| `SHORT_TERM_MEMORY_TYPE=inmemory` | Uses in-process MemorySaver instead of Redis (not persistent) |
| `MEMORY_SHORT_TERM_MESSAGE_LIMIT=10` | Trims message history to last 10 messages per LLM call |
| `MEMORY_LONG_TERM_RECALL_LIMIT=0` | Effectively disables recall (no summaries injected) |
