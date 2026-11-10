"""
Backend-owned data export (ADR Option B).

Produces authoritative CSV / Excel / PDF files from the real SQL result of a
stored conversation, by re-executing that conversation's persisted SQL against
the analytics database using the read-only agent DB user (RBAC-safe).

Why re-execute instead of parsing stored strings:
  - The LangChain SQL tool output is a stringified list of tuples WITHOUT column
    names, so it cannot be exported faithfully.
  - `query_log.sql_generated` holds the exact RBAC-filtered SELECT the agent ran.
    Re-running it yields real column names and the complete, untruncated result.

Security:
  - Only SELECT statements are allowed (defensive check; the stored SQL is already
    agent-generated and RBAC-constrained via the ca_agent_user grants).
  - CSV/Excel cells are sanitised against spreadsheet formula injection (ADR §4.1).
  - Row count is capped (EXPORT_MAX_ROWS) to bound memory / file size.
  - Every export is audit-logged (who, what conversation, format, row count).
"""

import csv
import io
import logging
import re
from datetime import datetime, timezone

import psycopg

from conversational_analytics.config import get_settings
from conversational_analytics.memory import audit_writer

logger = logging.getLogger(__name__)

# Guardrail: maximum rows to export in one file.
EXPORT_MAX_ROWS = 100_000

# Characters that trigger formula interpretation in Excel / Google Sheets.
_FORMULA_PREFIXES = ("=", "+", "-", "@")
_FORMULA_LEADING_CONTROL = ("\t", "\r")

SUPPORTED_FORMATS = ("csv", "xlsx", "pdf")

_MIME = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


class ExportError(Exception):
    """Raised for recoverable export failures (bad format, no data, etc.)."""


# ── Data access ───────────────────────────────────────────────────────

def _memory_conn_str() -> str:
    cfg = get_settings()
    return (
        f"host={cfg.long_term_memory_db_host} "
        f"port={cfg.long_term_memory_db_port} "
        f"dbname={cfg.long_term_memory_db_name} "
        f"user={cfg.long_term_memory_db_user} "
        f"password={cfg.long_term_memory_db_password}"
    )


async def _fetch_conversation(conversation_id: str) -> dict | None:
    """Loads the stored conversation metadata needed to export."""
    sql = """
        SELECT conversation_id, session_id, user_id, role, user_query, sql_generated
        FROM query_log
        WHERE conversation_id = %(cid)s
        LIMIT 1
    """
    async with await psycopg.AsyncConnection.connect(_memory_conn_str()) as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(sql, {"cid": conversation_id})
            return await cur.fetchone()


def _is_safe_select(sql: str) -> bool:
    """Defensive guard: allow a single read-only SELECT / WITH statement only."""
    if not sql:
        return False
    s = sql.strip().rstrip(";").strip()
    # Reject multiple statements.
    if ";" in s:
        return False
    head = s.lstrip("(").lstrip().lower()
    if not (head.startswith("select") or head.startswith("with")):
        return False
    # Reject obvious write/DDL keywords as whole words.
    forbidden = r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|copy)\b"
    if re.search(forbidden, s, flags=re.IGNORECASE):
        return False
    return True


async def _run_authoritative_query(sql: str) -> tuple[list[str], list[tuple]]:
    """Re-executes the stored SELECT against the analytics DB (read-only user).

    Returns (columns, rows). Caps rows at EXPORT_MAX_ROWS + 1 so callers can tell
    whether truncation happened.
    """
    cfg = get_settings()
    conn_str = (
        f"host={cfg.analytics_db_host} "
        f"port={cfg.analytics_db_port} "
        f"dbname={cfg.analytics_db_name} "
        f"user={cfg.analytics_db_user} "
        f"password={cfg.analytics_db_password}"
    )
    async with await psycopg.AsyncConnection.connect(conn_str) as conn:
        # Belt-and-braces: make the whole session read-only.
        await conn.execute("SET TRANSACTION READ ONLY")
        async with conn.cursor() as cur:
            await cur.execute(sql)
            columns = [d.name for d in cur.description] if cur.description else []
            rows = await cur.fetchmany(EXPORT_MAX_ROWS + 1)
    return columns, rows


# ── Formatting helpers ─────────────────────────────────────────────────

def _sanitise_cell(value) -> str:
    """Neutralises spreadsheet formula injection (ADR §4.1) for string cells.

    Numbers / None are returned as-is-string; strings whose first character is a
    formula trigger are prefixed with a single quote so the spreadsheet app treats
    them as literal text.
    """
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    s = str(value)
    if s and (s[0] in _FORMULA_PREFIXES or s[0] in _FORMULA_LEADING_CONTROL):
        return "'" + s
    return s


def _slug(text: str, fallback: str = "export") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60]
    return slug or fallback


def build_filename(conversation: dict, fmt: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    base = _slug(conversation.get("user_query") or "export")
    return f"{base}_{stamp}.{fmt}"


# ── File builders ───────────────────────────────────────────────────────

def _to_csv(columns: list[str], rows: list[tuple]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([_sanitise_cell(c) for c in columns])
    for row in rows:
        writer.writerow([_sanitise_cell(v) for v in row])
    # UTF-8 BOM so Excel opens non-ASCII correctly.
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


def _to_xlsx(columns: list[str], rows: list[tuple], title: str) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    ws.append([_sanitise_cell(c) for c in columns])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in rows:
        out = []
        for v in row:
            # Keep real numbers numeric; sanitise everything else to text.
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append(v)
            else:
                out.append(_sanitise_cell(v))
        ws.append(out)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _to_pdf(columns: list[str], rows: list[tuple], title: str) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), title=title)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title or "Export", styles["Title"]), Spacer(1, 12)]

    # PDF tables don't paginate huge datasets well; cap the rows shown.
    pdf_rows = rows[:2000]
    data = [[str(c) for c in columns]] + [[("" if v is None else str(v)) for v in r] for r in pdf_rows]

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d2d3a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f6")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(table)

    if len(rows) > len(pdf_rows):
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Showing first {len(pdf_rows):,} of {len(rows):,} rows. "
            f"Use CSV or Excel for the full dataset.",
            styles["Italic"],
        ))

    doc.build(elements)
    return buf.getvalue()


# ── Public entrypoint ───────────────────────────────────────────────────

async def export_conversation(
    conversation_id: str,
    fmt: str,
    requested_by: str | None = None,
    role: str | None = None,
) -> tuple[bytes, str, str]:
    """Builds an export file for a stored conversation.

    Returns (file_bytes, media_type, filename).
    Raises ExportError on bad input / missing data.
    """
    fmt = (fmt or "").lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(f"Unsupported format '{fmt}'. Use one of: {', '.join(SUPPORTED_FORMATS)}.")

    conversation = await _fetch_conversation(conversation_id)
    if conversation is None:
        raise ExportError(f"Conversation '{conversation_id}' not found.")

    sql = conversation.get("sql_generated")
    if not sql or not sql.strip():
        raise ExportError("This conversation has no exportable query result.")
    if not _is_safe_select(sql):
        logger.warning(f"Refusing to export non-SELECT SQL for conversation={conversation_id}")
        raise ExportError("The stored query is not a read-only SELECT and cannot be exported.")

    columns, rows = await _run_authoritative_query(sql)
    truncated = len(rows) > EXPORT_MAX_ROWS
    if truncated:
        rows = rows[:EXPORT_MAX_ROWS]
        logger.warning(f"Export truncated to {EXPORT_MAX_ROWS} rows for conversation={conversation_id}")

    if not columns:
        raise ExportError("The query returned no columns to export.")

    title = conversation.get("user_query") or "Export"

    if fmt == "csv":
        content = _to_csv(columns, rows)
    elif fmt == "xlsx":
        content = _to_xlsx(columns, rows, title)
    else:  # pdf
        content = _to_pdf(columns, rows, title)

    filename = build_filename(conversation, fmt)

    # ── Audit the export (who, what, format, row count) ──
    _audit_export(conversation, fmt, len(rows), requested_by, role, truncated)

    logger.info(
        f"Export built — conversation={conversation_id} format={fmt} "
        f"rows={len(rows)} cols={len(columns)} by={requested_by}"
    )
    return content, _MIME[fmt], filename


def _audit_export(conversation, fmt, row_count, requested_by, role, truncated) -> None:
    """Fire-and-forget audit record of the export via the existing audit writer."""
    try:
        cfg = get_settings()
        if not cfg.long_term_memory_enabled:
            return
        audit_writer.enqueue_agent_step(
            conversation_id=conversation["conversation_id"],
            session_id=conversation.get("session_id") or "",
            user_id=requested_by or conversation.get("user_id") or "",
            step_number=0,
            step_type="export",
            tool_name=fmt,
            output=(
                f"exported {row_count} rows as {fmt}"
                + (" (truncated)" if truncated else "")
                + (f" role={role}" if role else "")
            ),
        )
    except Exception as e:  # audit must never break the export
        logger.warning(f"Failed to enqueue export audit: {e}")
