import json
import logging
import psycopg
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


def _extract_activity(stream_events, stream_mode: str = "standard") -> list[dict]:
    """Maps persisted stream_events into the frontend 'activity' timeline shape,
    filtered by the requested stream_mode so history matches the live UX.

    Event types in the order they occurred:
      - `step`         sanitized, hardcoded progress labels (standard-mode runs)
      - `thinking`     raw model reasoning (verbose-mode runs only)
      - `tool_call`    tool name + arguments (verbose-mode runs only)
      - `tool_result`  tool output (verbose-mode runs only)

    stream_mode controls exposure:
      - "verbose":  returns everything recorded (thinking/tool_call/tool_result
                    and step).
      - "standard": returns ONLY the sanitized `step` entries and SUPPRESSES any
                    thinking/tool_call/tool_result. This enforces the standard-mode
                    safety contract even for conversations that were originally run
                    in verbose mode — no SQL/schema/raw reasoning leaks when the UI
                    is in standard mode.

    `response`/`done`/`error` are always omitted. A conversation that ran in
    standard mode has no verbose events stored, so requesting "verbose" simply
    returns its `step` entries (we cannot fabricate detail that was never captured).
    Returns [] when no relevant events were recorded.
    """
    if not stream_events:
        return []
    # psycopg may return a JSONB column already decoded, or as a JSON string.
    if isinstance(stream_events, str):
        try:
            stream_events = json.loads(stream_events)
        except (ValueError, TypeError):
            return []
    if not isinstance(stream_events, list):
        return []

    verbose = stream_mode == "verbose"
    activity: list[dict] = []
    for ev in stream_events:
        if not isinstance(ev, dict):
            continue
        kind = ev.get("event")
        if kind == "step":
            activity.append({"type": "step", "message": ev.get("message", "")})
        elif not verbose:
            # Standard mode: never expose raw thinking / tool details.
            continue
        elif kind == "thinking":
            activity.append({"type": "thinking", "reasoning": ev.get("reasoning", "")})
        elif kind == "tool_call":
            activity.append({"type": "tool_call", "tool": ev.get("tool"), "args": ev.get("args")})
        elif kind == "tool_result":
            activity.append({"type": "tool_result", "tool": ev.get("tool"), "output": ev.get("output")})
    return activity


def _get_conn_str() -> str:
    cfg = get_settings()
    return (
        f"host={cfg.long_term_memory_db_host} "
        f"port={cfg.long_term_memory_db_port} "
        f"dbname={cfg.long_term_memory_db_name} "
        f"user={cfg.long_term_memory_db_user} "
        f"password={cfg.long_term_memory_db_password}"
    )


async def get_session_list(
    user_id: str | None,
    page: int,
    page_size: int,
) -> dict:
    """
    Returns paginated list of sessions (grouped by session_id),
    ordered by latest activity descending.
    """
    offset = (page - 1) * page_size
    filters = "WHERE user_id = %(user_id)s" if user_id else ""
    params: dict = {"limit": page_size, "offset": offset}
    if user_id:
        params["user_id"] = user_id

    sql = f"""
        SELECT
            session_id,
            user_id,
            role,
            COUNT(*)                        AS total_conversations,
            MIN(created_at)                 AS session_start,
            MAX(created_at)                 AS last_activity,
            SUM(execution_ms)               AS total_execution_ms
        FROM query_log
        {filters}
        GROUP BY session_id, user_id, role
        ORDER BY last_activity DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    count_sql = f"""
        SELECT COUNT(DISTINCT session_id)
        FROM query_log
        {filters}
    """

    async with await psycopg.AsyncConnection.connect(_get_conn_str()) as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(count_sql, params)
            total = (await cur.fetchone())["count"]
            await cur.execute(sql, params)
            rows = await cur.fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "sessions": [
            {
                "session_id":           r["session_id"],
                "user_id":              r["user_id"],
                "role":                 r["role"],
                "total_conversations":  r["total_conversations"],
                "session_start":        r["session_start"].isoformat() if r["session_start"] else None,
                "last_activity":        r["last_activity"].isoformat() if r["last_activity"] else None,
                "total_execution_ms":   r["total_execution_ms"],
            }
            for r in rows
        ],
    }


async def get_session_detail(
    session_id: str,
    page: int,
    page_size: int,
    stream_mode: str = "standard",
) -> dict:
    """
    Returns paginated conversations within a session,
    ordered by created_at descending (latest first).
    """
    offset = (page - 1) * page_size
    params: dict = {"session_id": session_id, "limit": page_size, "offset": offset}

    sql = """
        SELECT
            conversation_id,
            user_query,
            agent_response,
            has_vega,
            vega_spec,
            stream_events,
            execution_ms,
            created_at
        FROM query_log
        WHERE session_id = %(session_id)s
        ORDER BY created_at DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    count_sql = """
        SELECT COUNT(*) FROM query_log WHERE session_id = %(session_id)s
    """

    meta_sql = """
        SELECT
            user_id,
            role,
            MIN(created_at) AS session_start,
            MAX(created_at) AS last_activity,
            COUNT(*)        AS total_conversations
        FROM query_log
        WHERE session_id = %(session_id)s
        GROUP BY user_id, role
    """

    async with await psycopg.AsyncConnection.connect(_get_conn_str()) as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(count_sql, params)
            total = (await cur.fetchone())["count"]

            if total == 0:
                return None

            await cur.execute(meta_sql, {"session_id": session_id})
            meta = await cur.fetchone()

            await cur.execute(sql, params)
            rows = await cur.fetchall()

    return {
        "session_id":           session_id,
        "user_id":              meta["user_id"],
        "role":                 meta["role"],
        "session_start":        meta["session_start"].isoformat() if meta["session_start"] else None,
        "last_activity":        meta["last_activity"].isoformat() if meta["last_activity"] else None,
        "total_conversations":  total,
        "page":                 page,
        "page_size":            page_size,
        "total_pages":          max(1, -(-total // page_size)),
        "conversations": [
            {
                "conversation_id": str(r["conversation_id"]),
                "user_query":      r["user_query"],
                "agent_response":  r["agent_response"],
                "has_vega":        r["has_vega"],
                "vega_spec":       r["vega_spec"],
                "activity":        _extract_activity(r.get("stream_events"), stream_mode),
                "execution_ms":    r["execution_ms"],
                "created_at":      r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ],
    }
