-- ─────────────────────────────────────────────────────────────────────────────
-- Long-Term Memory Schema
--
-- Architecture:
--   Short-term : Redis (RedisSaver checkpointer) — per-session graph state
--   Long-term  : PostgreSQL (LangGraph PostgresStore) — cross-session memory
--
-- LangGraph manages its own table:
--   public.store  (prefix, key, value, created_at, updated_at, expires_at)
--   Created automatically by PostgresStore.setup()
--
-- This migration adds:
--   1. memory.query_log  — audit trail of every query
--   2. Views over public.store for easy querying
-- ─────────────────────────────────────────────────────────────────────────────

CREATE SCHEMA IF NOT EXISTS memory;

-- ── 1. Query audit log ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS memory.query_log (
    id              BIGSERIAL   PRIMARY KEY,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    role            TEXT,
    user_query      TEXT        NOT NULL,
    sql_generated   TEXT,
    tools_invoked   TEXT[],
    has_vega        BOOLEAN     NOT NULL DEFAULT FALSE,
    execution_ms    INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_query_log_user_id
    ON memory.query_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_log_session_id
    ON memory.query_log(session_id, created_at DESC);

-- ── 2. Views over public.store ────────────────────────────────────────────────
-- LangGraph stores data as: prefix = 'namespace.user_id', key, value (JSONB)

CREATE OR REPLACE VIEW memory.conversation_history AS
SELECT
    split_part(prefix, '.', 2)  AS user_id,
    key                          AS turn_key,
    value->>'query'              AS user_query,
    value->>'response'           AS response,
    value->>'role'               AS role,
    value->'tools_invoked'       AS tools_invoked,
    (value->>'has_vega')::bool   AS has_vega,
    created_at,
    updated_at
FROM public.store
WHERE prefix LIKE 'conversation_history.%';

CREATE OR REPLACE VIEW memory.query_history_store AS
SELECT
    split_part(prefix, '.', 2)  AS user_id,
    key                          AS query_key,
    value->>'content'            AS user_query,
    value->>'role'               AS role,
    value->>'session_id'         AS session_id,
    created_at
FROM public.store
WHERE prefix LIKE 'query_history.%';

CREATE OR REPLACE VIEW memory.user_memories AS
SELECT
    split_part(prefix, '.', 2)  AS user_id,
    key,
    value->>'content'            AS content,
    created_at,
    updated_at
FROM public.store
WHERE prefix LIKE 'user_memory.%';
