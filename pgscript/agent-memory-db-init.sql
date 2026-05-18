-- ─────────────────────────────────────────────────────────────────────────────
-- Agent Memory Database Initialisation
--
-- Tables created here (in public schema):
--   store        — LangGraph AsyncPostgresStore documents (pre-created to avoid setup() DDL lock)
--   store_vectors — pgvector embeddings for semantic search
--   query_log    — audit trail of every conversation
--   agent_steps  — audit trail of every ReAct step
-- ─────────────────────────────────────────────────────────────────────────────

CREATE EXTENSION IF NOT EXISTS vector;

-- ── 1. LangGraph AsyncPostgresStore tables ────────────────────────────────────
-- Pre-created so AsyncPostgresStore.setup() is a no-op and never blocks on DDL.
CREATE TABLE IF NOT EXISTS store (
    prefix      TEXT             NOT NULL,
    key         TEXT             NOT NULL,
    value       JSONB            NOT NULL,
    created_at  TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    ttl_minutes DOUBLE PRECISION,
    PRIMARY KEY (prefix, key)
);

CREATE TABLE IF NOT EXISTS store_vectors (
    prefix      TEXT        NOT NULL,
    key         TEXT        NOT NULL,
    field_name  TEXT        NOT NULL,
    embedding   vector(768),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (prefix, key, field_name)
);

CREATE INDEX IF NOT EXISTS idx_store_vectors_embedding
    ON store_vectors USING hnsw (embedding vector_cosine_ops);

-- ── 2. Query audit log ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS query_log (
    id              BIGSERIAL   PRIMARY KEY,
    conversation_id UUID        NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    role            TEXT,
    user_query      TEXT        NOT NULL,
    prompt          TEXT,
    sql_generated   TEXT,
    tools_invoked   TEXT[],
    agent_response  TEXT,
    vega_spec       JSONB,
    vega_specs      JSONB,
    token_usage     JSONB,
    stream_events   JSONB,
    has_vega        BOOLEAN     NOT NULL DEFAULT FALSE,
    execution_ms    INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_query_log_user_id
    ON query_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_log_session_id
    ON query_log(session_id, created_at DESC);

-- ── 3. Agent steps log ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_steps (
    id              BIGSERIAL   PRIMARY KEY,
    conversation_id UUID        NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    step_number     INT         NOT NULL,
    step_type       TEXT        NOT NULL,
    tool_name       TEXT,
    input           TEXT,
    output          TEXT,
    token_usage     JSONB,
    duration_ms     INT,
    prompt          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_steps_conversation_id
    ON agent_steps(conversation_id, step_number ASC);

CREATE INDEX IF NOT EXISTS idx_agent_steps_session_id
    ON agent_steps(session_id, created_at DESC);
