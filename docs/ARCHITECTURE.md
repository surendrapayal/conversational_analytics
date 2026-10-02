# System Architecture

## Overview

Conversational Analytics is a natural language query (NLQ) system built for restaurant management. It allows users to ask plain-English questions about their restaurant data and receive structured answers, data tables, and auto-generated charts — all backed by a live PostgreSQL database.

The backend is a Python FastAPI application that uses a LangGraph ReAct agent powered by Google Gemini (via Vertex AI). The agent translates natural language into SQL, executes it against the analytics database, and returns a formatted response with an optional Vega-Lite chart specification.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        React / Vite Frontend                        │
│                        (localhost:3000)                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTP / SSE  (POST /api/v1/stream)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend  (localhost:8000)               │
│                                                                     │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────┐  │
│  │ NLQ          │   │ History          │   │ CORS / Lifespan    │  │
│  │ Controller   │   │ Controller       │   │ Middleware         │  │
│  └──────┬───────┘   └────────┬─────────┘   └────────────────────┘  │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐   ┌──────────────────┐                           │
│  │ Agent        │   │ History          │                           │
│  │ Service      │   │ Service          │                           │
│  └──────┬───────┘   └────────┬─────────┘                           │
│         │                   │                                       │
└─────────┼───────────────────┼─────────────────────────────────────-┘
          │                   │
          ▼                   ▼
┌─────────────────┐   ┌───────────────────────────────────────────────┐
│  LangGraph      │   │  PostgreSQL (zenvyra)                         │
│  ReAct Graph    │   │  ├── Analytics tables (orders, payments, …)   │
│  (Agent Loop)   │   │  ├── query_log  (audit trail)                 │
└────────┬────────┘   │  ├── agent_steps (step audit)                 │
         │            │  ├── store       (LangGraph long-term memory) │
         │            │  └── store_vectors (pgvector embeddings)      │
         ▼            └───────────────────────────────────────────────┘
┌─────────────────┐
│  Google Gemini  │   ┌───────────────────────────────────────────────┐
│  (Vertex AI)    │   │  Redis                                        │
│  gemini-2.0-    │   │  Short-term session memory                    │
│  flash          │   │  (LangGraph AsyncRedisSaver checkpointer)     │
└─────────────────┘   └───────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. FastAPI Application (`main.py`)

The entry point. Responsibilities:
- Configures the asyncio event loop (Windows requires `SelectorEventLoop` for psycopg async).
- Registers CORS middleware allowing the frontend at `localhost:3000`.
- Manages application lifespan: starts the `AuditWriter` background worker and initialises the LangGraph graph on startup; gracefully drains the audit queue on shutdown.
- Mounts two routers: `NLQ Controller` and `History Controller`.

### 2. NLQ Controller (`controller/nlq_controller.py`)

Exposes two endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/chat` | POST | Synchronous — waits for full agent response |
| `/api/v1/stream` | POST | Streaming — returns Server-Sent Events (SSE) |

Both endpoints:
- Accept `X-Session-Id` header (auto-generated if absent) to maintain conversation continuity.
- Accept a `role` header to enforce role-based data access.
- Sanitise input using `nh3` to strip HTML/script injection.
- Validate query length (5–1000 characters).

### 3. Agent Service (`controller/agent_service.py`)

Orchestrates the LangGraph graph execution. Two modes:

**`run_agent`** — synchronous mode: streams the graph internally, collects the final state, returns a complete `AgentResponse`.

**`stream_agent`** — SSE streaming mode: yields SSE events in real time as the graph executes:

| SSE Event | When emitted |
|---|---|
| `step` | Each tool call (human-readable label) |
| `tool_call` | Verbose mode — raw tool name + args |
| `tool_result` | Verbose mode — raw tool output |
| `thinking` | Verbose mode — Gemini reasoning trace |
| `response` | Final answer text + optional Vega spec |
| `done` | Execution complete |
| `error` | On exception |

After execution, `_persist_audit` is fired as a non-blocking `asyncio.create_task` to write the audit log and save the conversation summary without blocking the response.

### 4. History Controller & Service (`controller/history_controller.py`, `history_service.py`)

Exposes two read-only endpoints backed by the `query_log` table:

| Endpoint | Description |
|---|---|
| `GET /api/v1/sessions` | Paginated list of sessions, grouped by `session_id`, ordered by latest activity |
| `GET /api/v1/sessions/{session_id}` | Paginated conversations within a session |

Uses `psycopg` async connections directly (no ORM).

### 5. LangGraph ReAct Graph (`graph/graph.py`)

The core reasoning engine. A directed graph with three nodes:

```
[agent] ──── has tool calls? ──── YES ──→ [tools] ──→ [agent]  (loop)
                                  NO  ──→ [response_formatter] ──→ END
```

- Compiled with an `AsyncRedisSaver` checkpointer (short-term memory) and an `AsyncPostgresStore` (long-term memory).
- The `thread_id` in the LangGraph config is set to `session_id`, so all turns within a session share the same checkpoint.

### 6. Agent Node (`nlq_agent/nodes/nodes.py`)

The LLM reasoning step. On each invocation:
1. Loads the role-specific SQL tools and system message.
2. On the **first turn** of a request (no tools invoked yet), performs a semantic search over past conversations to inject relevant memory context into the system prompt.
3. Enforces `agent_max_iterations` — if the limit is reached, forces a final response without tools.
4. Optionally trims the message history to `memory_short_term_message_limit` to control context window size.
5. Calls `get_llm().bind_tools(tools).invoke(...)` and returns the AI message.

### 7. Tools Node (`nlq_agent/nodes/nodes.py`)

Wraps LangGraph's `ToolNode`. Executes whichever SQL tools the LLM requested, collects `ToolMessage` results, and appends them to the state for the next agent iteration.

### 8. Response Formatter Node (`nlq_agent/nodes/nodes.py`)

Post-processes the final AI message:
- Extracts plain text from Gemini's list-of-parts content format.
- Detects and parses a `vega` fenced code block from the response.
- Validates the Vega-Lite spec (supports `mark`, `layer`, `spec`, `hconcat`, `vconcat`, `concat`).
- Returns `final_response` (clean text) and `vega_spec` (parsed dict or `None`).

### 9. SQL Tools (`nlq_agent/tools/sql_tools.py`)

Builds and caches role-specific SQL database contexts at startup. Each context contains:
- A `SQLDatabase` instance (LangChain) connected to the analytics DB with the correct table visibility.
- A `SQLDatabaseToolkit` providing four tools: `sql_db_list_tables`, `sql_db_schema`, `sql_db_query_checker`, `sql_db_query`.
- A `SystemMessage` with the full system prompt including the semantic layer.

Role contexts are built once at module load and cached in `_role_cache`. Unknown roles raise a `ValueError`.

### 10. LLM (`llm/llm.py`)

Returns a `ChatGoogleGenerativeAI` instance using Vertex AI Application Default Credentials (ADC). Configured via `.env`:
- Model: `gemini-2.0-flash`
- Thinking level: `medium` (enables chain-of-thought reasoning)
- Safety settings: blocks medium-and-above harmful content across all categories.

### 11. Semantic Layer (`semantic/semantic_layer.py`)

Loads `semantic_layer.json` once (cached with `lru_cache`) and injects business context into the system prompt. Provides:
- Global business rules
- Role-specific description and guidelines
- Critical SQL filter patterns
- Key join patterns with notes
- Available metrics with units, filtered to the role's allowed domains

### 12. Configuration (`config.py`)

A `pydantic-settings` `BaseSettings` class. Reads all configuration from `.env`. Key features:
- Role-based table access: `ROLE_<NAME>=table1,table2` env vars are auto-discovered.
- Role-based column restrictions: `ROLE_<NAME>_RESTRICT_COLUMNS=table.col,...`
- Role-based row filters: `ROLE_<NAME>_ROW_FILTERS=table:condition,...`
- Mutually exclusive `DB_IGNORE_TABLES` / `DB_INCLUDE_TABLES` validation.
- Singleton via `@lru_cache` on `get_settings()`.

---

## Data Flow: A Single Query

```
User types: "Show top 10 best-selling menu items"
     │
     ▼
POST /api/v1/stream  {user_id, query, stream_mode: "standard"}
     │  Headers: X-Session-Id, role
     │
     ▼
nlq_controller.stream()
  → builds AgentRequest (session_id, conversation_id, role, query)
  → returns StreamingResponse wrapping stream_agent()
     │
     ▼
stream_agent() — iterates graph.astream()
     │
     ├─ [agent node]
     │    ├─ semantic search → inject past context (first turn only)
     │    ├─ LLM decides: call sql_db_list_tables
     │    └─ yields SSE: event:step  data:{"message":"Identifying available data sources"}
     │
     ├─ [tools node] → executes sql_db_list_tables → returns table list
     │
     ├─ [agent node] → LLM decides: call sql_db_schema
     │    └─ yields SSE: event:step  data:{"message":"Analysing data structure"}
     │
     ├─ [tools node] → executes sql_db_schema → returns schema
     │
     ├─ [agent node] → LLM decides: call sql_db_query_checker
     │    └─ yields SSE: event:step  data:{"message":"Validating query"}
     │
     ├─ [tools node] → executes sql_db_query_checker → validates SQL
     │
     ├─ [agent node] → LLM decides: call sql_db_query
     │    └─ yields SSE: event:step  data:{"message":"Retrieving data"}
     │
     ├─ [tools node] → executes sql_db_query → returns result rows
     │
     ├─ [agent node] → LLM generates final answer (no more tool calls)
     │
     ├─ [response_formatter] → extracts text + Vega spec
     │    └─ yields SSE: event:response  data:{"text":"...", "vega_spec":{...}}
     │
     └─ yields SSE: event:done  data:{"status":"completed"}
          │
          └─ asyncio.create_task(_persist_audit(...))
               ├─ audit_writer.enqueue_query_log(...)   ← non-blocking
               └─ save_conversation_summary(...)        ← async, saves embedding
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn |
| Agent framework | LangGraph (ReAct graph) |
| LLM | Google Gemini 2.0 Flash (Vertex AI) |
| LLM client | LangChain Google GenAI |
| SQL toolkit | LangChain SQLDatabaseToolkit |
| Analytics DB | PostgreSQL 15+ (port 5433) |
| Short-term memory | Redis (LangGraph AsyncRedisSaver) |
| Long-term memory | PostgreSQL + pgvector (LangGraph AsyncPostgresStore) |
| Embeddings | Google `text-embedding-005` (768 dims, Vertex AI) |
| Async DB driver | psycopg3 (async) + psycopg-pool |
| Input sanitisation | nh3 |
| Config management | pydantic-settings |
| Package manager | uv |
