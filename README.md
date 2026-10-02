# Conversational Analytics

A full-stack conversational analytics application for restaurant management. Users ask plain-English questions about their restaurant data and receive structured answers, data tables, and auto-generated charts — all backed by a live PostgreSQL database.

The backend is a Python FastAPI application using a LangGraph ReAct agent powered by Google Gemini (Vertex AI). The agent translates natural language into SQL, executes it, and returns a formatted response with an optional Vega-Lite chart.

---

## Prerequisites

- Python (with `uv` package manager)
- Node.js & npm
- PostgreSQL running on port `5433` with database `zenvyra`
- Redis running on port `6379` (for short-term session memory)
- Google Cloud project with Vertex AI enabled and Application Default Credentials configured

---

## Starting the Application

### 1. Backend (FastAPI)

```bash
cd conversational-analytics
uv run uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`.
Interactive API docs at `http://localhost:8000/docs`.

### 2. Frontend (React/Vite)

In a separate terminal:

```bash
cd conversational-analytics/conversational-analytics-ui
npm install   # first time only
npm run dev
```

UI will be available at `http://localhost:3000`.

> The frontend proxies all `/api` requests to the backend at `http://localhost:8000`.

---

## Login

Use one of the built-in POC accounts:

| Username  | Password     | Role             |
|-----------|--------------|------------------|
| admin     | admin123     | admin            |
| gm        | gm123        | general_manager  |
| manager   | manager123   | location_manager |
| chef      | chef123      | chef             |
| waiter    | waiter123    | waiter           |
| cashier   | cashier123   | cashier          |
| analyst   | analyst123   | analyst          |

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Full system architecture, component breakdown, data flow, and technology stack |
| [Memory Architecture](docs/MEMORY_ARCHITECTURE.md) | Three-tier memory system: Redis short-term, PostgreSQL+pgvector long-term, audit log |
| [Agent & ReAct Loop](docs/AGENT_REACT_LOOP.md) | LangGraph ReAct graph, SQL tools, system prompt, Vega chart generation |
| [Role-Based Access Control](docs/RBAC.md) | Table-level, column-level, and row-level access control per role |
| [Database Schema](docs/DATABASE_SCHEMA.md) | Full analytics DB schema and agent memory schema |
| [API Reference](docs/API_REFERENCE.md) | All REST endpoints, request/response formats, SSE event types |
| [Configuration](docs/CONFIGURATION.md) | All `.env` variables with defaults and descriptions |
| [Sample Questions](docs/SAMPLE_QUESTIONS.md) | Example queries per role |
| [Daily Data Guide](docs/DAILY_DATA_GUIDE.md) | Test data generation guide |
