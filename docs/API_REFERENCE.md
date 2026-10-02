# API Reference

## Base URL
```
http://localhost:8000
```

Interactive docs available at `http://localhost:8000/docs` (Swagger UI).

---

## NLQ Agent Endpoints

### POST `/api/v1/chat`
Synchronous query — waits for the full agent response before returning.

**Request Headers**

| Header | Required | Description |
|---|---|---|
| `Content-Type` | Yes | `application/json` |
| `X-Session-Id` | No | Session UUID for conversation continuity. Auto-generated if absent. |
| `role` | No | User role for RBAC (e.g. `chef`, `waiter`, `analyst`) |

**Request Body**
```json
{
  "user_id": "analyst",
  "query": "What is the net sales in each location?",
  "stream_mode": "standard"
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `user_id` | string | Yes | 1–100 chars, no HTML |
| `query` | string | Yes | 5–1000 chars, no HTML/script |
| `stream_mode` | string | No | `"standard"` or `"verbose"` (ignored for `/chat`) |

**Response Body**
```json
{
  "response_text": "Here is the net sales breakdown by location:\n\n| Location | Net Sales |\n|---|---|\n| Downtown | $45,230.00 |\n...",
  "vega_spec": {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "width": 700,
    "height": 400,
    "title": "Net Sales by Location",
    "mark": "bar",
    ...
  },
  "metadata": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
  }
}
```

**Response Headers**

| Header | Description |
|---|---|
| `X-Session-Id` | The session ID used (echo back or newly generated) |

---

### POST `/api/v1/stream`
Streaming query — returns Server-Sent Events (SSE) as the agent executes.

**Request Headers** — same as `/chat`.

**Request Body** — same as `/chat`. `stream_mode` is used here:
- `"standard"` — emits `step` events with human-readable labels
- `"verbose"` — additionally emits `tool_call`, `tool_result`, and `thinking` events

**Response**
- Content-Type: `text/event-stream`
- Header: `X-Accel-Buffering: no` (disables nginx buffering)
- Header: `X-Session-Id: <session_id>`

**SSE Event Types**

#### `step` (standard mode)
Emitted when the LLM decides to call a tool. Human-readable progress indicator.
```
event: step
data: {"message": "Identifying available data sources", "session_id": "...", "conversation_id": "...", "timestamp": "2026-05-25T10:30:00Z"}
```

Tool → Label mapping:
| Tool | Label |
|---|---|
| `sql_db_list_tables` | Identifying available data sources |
| `sql_db_schema` | Analysing data structure |
| `sql_db_query_checker` | Validating query |
| `sql_db_query` | Retrieving data |

#### `tool_call` (verbose mode only)
```
event: tool_call
data: {"tool": "sql_db_query", "args": {"query": "SELECT ..."}, "session_id": "...", ...}
```

#### `tool_result` (verbose mode only)
```
event: tool_result
data: {"tool": "sql_db_query", "output": "location_name | net_sales\n...", "session_id": "...", ...}
```

#### `thinking` (verbose mode only)
Gemini chain-of-thought reasoning trace.
```
event: thinking
data: {"reasoning": "The user wants net sales per location. I should join orders with locations...", ...}
```

#### `response`
The final answer. Always emitted once before `done`.
```
event: response
data: {
  "text": "Here is the net sales breakdown...",
  "vega_spec": { "$schema": "...", "mark": "bar", ... },
  "session_id": "...",
  "conversation_id": "...",
  "timestamp": "..."
}
```
`vega_spec` is `null` if no chart was generated.

#### `done`
Signals end of stream.
```
event: done
data: {"status": "completed", "session_id": "...", "conversation_id": "...", "timestamp": "..."}
```
On error: `"status": "failed"`.

#### `error`
Emitted on exception, followed by `done`.
```
event: error
data: {"message": "Error description", "session_id": "...", ...}
```

---

## History Endpoints

### GET `/api/v1/sessions`
Returns a paginated list of sessions ordered by latest activity descending.

**Query Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `user_id` | string | — | Filter sessions by user ID |
| `page` | int | 1 | Page number (≥1) |
| `page_size` | int | 20 | Results per page (1–100) |

**Response**
```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "sessions": [
    {
      "session_id": "550e8400-...",
      "user_id": "analyst",
      "role": "analyst",
      "total_conversations": 7,
      "session_start": "2026-05-25T09:00:00+00:00",
      "last_activity": "2026-05-25T10:45:00+00:00",
      "total_execution_ms": 18420
    }
  ]
}
```

---

### GET `/api/v1/sessions/{session_id}`
Returns paginated conversations within a session, ordered by latest first.

**Path Parameters**

| Parameter | Description |
|---|---|
| `session_id` | Session UUID |

**Query Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page (1–100) |

**Response**
```json
{
  "session_id": "550e8400-...",
  "user_id": "analyst",
  "role": "analyst",
  "session_start": "2026-05-25T09:00:00+00:00",
  "last_activity": "2026-05-25T10:45:00+00:00",
  "total_conversations": 7,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "conversations": [
    {
      "conversation_id": "6ba7b810-...",
      "user_query": "What is the net sales in each location?",
      "agent_response": "Here is the net sales breakdown...",
      "has_vega": true,
      "vega_spec": { "$schema": "...", ... },
      "execution_ms": 3240,
      "created_at": "2026-05-25T10:45:00+00:00"
    }
  ]
}
```

Returns `404` if the session does not exist.

---

## Error Responses

All endpoints return standard HTTP error responses:

| Status | Cause |
|---|---|
| `400` | Validation error (query too short/long, invalid characters) |
| `404` | Session not found |
| `500` | Agent error or database error |

```json
{
  "detail": "Error description"
}
```

---

## Input Validation & Security

- All string inputs are sanitised with `nh3` — HTML tags and script content are stripped.
- If the sanitised value differs from the original input, a `400` validation error is returned.
- Query length: minimum 5 characters, maximum 1000 characters.
- User ID length: maximum 100 characters.
- The agent is instructed via system prompt to only execute read-only SELECT queries. INSERT, UPDATE, DELETE, DROP, TRUNCATE, and ALTER are explicitly forbidden.
