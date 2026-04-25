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
    token_usage     JSONB,
    stream_events   JSONB,
    has_vega        BOOLEAN     NOT NULL DEFAULT FALSE,
    execution_ms    INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add new columns if table already exists (idempotent)
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS agent_response TEXT;
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS vega_spec JSONB;
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS token_usage JSONB;
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS conversation_id UUID;
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS prompt TEXT;
ALTER TABLE memory.query_log ADD COLUMN IF NOT EXISTS stream_events JSONB;

CREATE INDEX IF NOT EXISTS idx_query_log_user_id
    ON memory.query_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_log_session_id
    ON memory.query_log(session_id, created_at DESC);

-- ── 2. Agent steps log ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS memory.agent_steps (
    id              BIGSERIAL   PRIMARY KEY,
    conversation_id UUID        NOT NULL,
    session_id      TEXT        NOT NULL,
    user_id         TEXT        NOT NULL,
    step_number     INT         NOT NULL,   -- sequential step within the conversation
    step_type       TEXT        NOT NULL,   -- llm_call | tool_call | tool_result
    tool_name       TEXT,                   -- e.g. sql_db_query (null for llm_call)
    input           TEXT,                   -- tool args or LLM prompt summary
    output          TEXT,                   -- tool result or LLM response summary
    token_usage     JSONB,                  -- per-step token usage (llm_call only)
    duration_ms     INT,                    -- time taken for this step
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_steps_conversation_id
    ON memory.agent_steps(conversation_id, step_number ASC);

CREATE INDEX IF NOT EXISTS idx_agent_steps_session_id
    ON memory.agent_steps(session_id, created_at DESC);

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

-- Drop and recreate conversation_summaries view (renamed from session_summaries)
DROP VIEW IF EXISTS memory.session_summaries;
DROP VIEW IF EXISTS memory.conversation_summaries;
CREATE VIEW memory.conversation_summaries AS
SELECT
    split_part(prefix, '.', 2)      AS user_id,
    key                              AS conversation_id,
    value->>'session_id'             AS session_id,
    value->>'summary'                AS summary,
    value->>'role'                   AS role,
    created_at,
    updated_at
FROM public.store
WHERE prefix LIKE 'conversation_summaries.%';
