# Memory Architecture

## Overview

The system uses a two-layer memory architecture following the LangGraph production pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Request                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │      LangGraph Graph     │
              │  checkpointer= (Redis)   │  ← Short-term
              │  store= (PostgreSQL)     │  ← Long-term
              └─────────────────────────┘
```

---

## Short-Term Memory — Redis (RedisSaver)

### What it stores
Full LangGraph graph state for the **current session** only:
- All messages in the conversation thread
- Tool call results
- Intermediate reasoning steps
- Final response

### How it works
```
Request (session_id=abc) → graph.invoke(config={"thread_id": "abc"})
                         → RedisSaver loads state for thread "abc"
                         → Graph executes nodes
                         → RedisSaver saves state after every node
                         → Next request with same session_id resumes from saved state
```

### Configuration (.env)
```ini
REDIS_URL=redis://localhost:6379
REDIS_SESSION_TTL=3600   # seconds — state expires after 1 hour of inactivity
```

### Key properties
| Property | Value |
|---|---|
| Scope | One thread (session_id) |
| Managed by | LangGraph automatically |
| Latency | Sub-millisecond |
| Expiry | TTL-based (auto-cleanup) |
| Access pattern | By `thread_id` only |

### Where it's wired
`src/conversational_analytics/memory/memory.py` → `get_checkpointer()`
`src/conversational_analytics/graph/graph.py` → `graph.compile(checkpointer=...)`

---

## Long-Term Memory — PostgreSQL (PostgresStore)

### What it stores
Distilled facts and conversation history **across all sessions** for a user:
- Conversation Q&A turns (query + response summary)
- User preferences learned over time
- Any facts explicitly stored by nodes

### How it works
```
agent_node runs:
  → store.search(("conversation_history", user_id))  ← recall past turns
  → inject into system prompt as context

response_formatter_node runs:
  → store.put(("conversation_history", user_id), key, value)  ← save this turn
```

### Storage location
LangGraph creates and manages a `public.store` table in PostgreSQL:

```sql
-- LangGraph native table (managed automatically)
public.store (prefix, key, value, created_at, updated_at, expires_at)

-- prefix format: "namespace.user_id"
-- Examples:
--   conversation_history.user_001
--   user_memory.user_001
```

### Namespaces used
| Namespace | Key format | Content |
|---|---|---|
| `conversation_history` | `turn_{timestamp}` | Q&A pair, tools used, has_vega |
| `user_memory` | custom key | Learned preferences, facts |

### Configuration (.env)
```ini
# Long-term memory database — can be same or different from analytics DB
MEMORY_DB_HOST=localhost
MEMORY_DB_PORT=5433
MEMORY_DB_NAME=zenvyra
MEMORY_DB_USER=admin_user
MEMORY_DB_PASSWORD=admin_password
```

### Key properties
| Property | Value |
|---|---|
| Scope | Cross-session, per user_id |
| Managed by | Nodes explicitly via `store.put()` / `store.search()` |
| Latency | ~5-20ms (PostgreSQL) |
| Expiry | Indefinite (no TTL by default) |
| Access pattern | By `(namespace, user_id)` + semantic search |

### Where it's wired
`src/conversational_analytics/memory/long_term_memory.py` → `get_long_term_store()`
`src/conversational_analytics/graph/graph.py` → `graph.compile(store=...)`
`src/conversational_analytics/nlq_agent/nodes/nodes.py` → `agent_node(store)`, `response_formatter_node(store)`

---

## Query Audit Log — PostgreSQL (memory.query_log)

Separate from the LangGraph store — a structured audit trail of every query.

### Schema
```sql
memory.query_log (
    id              BIGSERIAL PRIMARY KEY,
    session_id      TEXT,
    user_id         TEXT,
    role            TEXT,
    user_query      TEXT,       -- original NLQ
    sql_generated   TEXT,       -- SQL that was executed
    tools_invoked   TEXT[],     -- list of tools called
    has_vega        BOOLEAN,    -- whether a chart was generated
    execution_ms    INT,        -- total response time
    created_at      TIMESTAMPTZ
)
```

### Convenience views
```sql
-- All conversation turns per user
SELECT * FROM memory.conversation_history WHERE user_id = 'user_001';

-- All queries per user
SELECT * FROM memory.query_history_store WHERE user_id = 'user_001';

-- User memories
SELECT * FROM memory.user_memories WHERE user_id = 'user_001';

-- Audit log
SELECT * FROM memory.query_log ORDER BY created_at DESC LIMIT 10;
```

---

## Decision Matrix

| Dimension | Short-Term (Redis) | Long-Term (PostgreSQL) |
|---|---|---|
| Scope | One session | All sessions for a user |
| LangGraph role | `checkpointer=` | `store=` |
| Managed by | LangGraph automatically | Nodes explicitly |
| Retrieval | By `thread_id` | By `(namespace, user_id)` |
| Expiry | TTL (e.g. 1 hour) | Indefinite |
| Latency | <1ms | 5-20ms |
| Use case | Current conversation state | Cross-session memory |

---

## Data Flow Per Request

```
1. Request arrives (user_id, session_id, query, role)
   │
2. agent_node (first call only — tools_invoked is empty)
   ├── store.search(("conversation_history", user_id))  → recall past 5 turns
   └── inject history into system prompt
   │
3. agent_node → tools_node → agent_node (ReAct loop)
   └── Redis checkpointer saves state after every node
   │
4. response_formatter_node
   ├── store.put(("conversation_history", user_id), turn_key, {...})  → save Q&A
   └── return final_response + vega_spec
   │
5. agent_service.run_agent
   └── log_query(...)  → write to memory.query_log (audit)
```

---

## External Database Setup

To use a **separate** PostgreSQL instance for long-term memory (recommended for production):

```ini
# .env — point memory DB to a different host/database
MEMORY_DB_HOST=memory-db.internal
MEMORY_DB_PORT=5432
MEMORY_DB_NAME=analytics_memory
MEMORY_DB_USER=memory_user
MEMORY_DB_PASSWORD=memory_password

# Analytics DB remains unchanged
DB_HOST=analytics-db.internal
DB_PORT=5432
DB_NAME=zenvyra
```

The schema is created automatically on startup via `setup_schema()` in `main.py`.

---

## Adding Custom Memories

To store a user preference from any node:

```python
# In any node that receives store: BaseStore
store.put(
    ("user_memory", user_id),
    "preferred_chart_type",
    {"content": "bar", "learned_from": "user explicitly asked for bar charts"}
)
```

To retrieve it in the next session:

```python
memories = store.search(("user_memory", user_id), limit=10)
for m in memories:
    print(m.key, m.value["content"])
```
