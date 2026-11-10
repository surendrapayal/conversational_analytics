import logging
from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, Response, Header

from conversational_analytics.controller.export_service import (
    export_conversation,
    ExportError,
    SUPPORTED_FORMATS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/conversations", tags=["Export"])


@router.get("/{conversation_id}/export")
async def export_conversation_data(
    conversation_id: str,
    format: Literal["csv", "xlsx", "pdf"] = Query(
        "csv", description=f"Export format: one of {', '.join(SUPPORTED_FORMATS)}"
    ),
    user_id: str | None = Query(None, description="Requesting user (for audit)"),
    role: str | None = Header(None, description="Caller role (for audit / RBAC)"),
):
    """
    Exports the authoritative SQL result of a stored conversation as a file.

    The result is produced by re-executing the conversation's persisted SQL
    against the analytics database with the read-only agent user — so the file
    reflects the real, RBAC-filtered query output, not what was rendered in the
    chart or summarised in the answer. Every export is audit-logged.
    """
    try:
        content, media_type, filename = await export_conversation(
            conversation_id=conversation_id,
            fmt=format,
            requested_by=user_id,
            role=role,
        )
    except ExportError as e:
        # Client-facing, recoverable errors.
        msg = str(e)
        status = 404 if "not found" in msg.lower() else 400
        raise HTTPException(status_code=status, detail=msg)
    except Exception as e:
        logger.error(
            f"Export failed for conversation={conversation_id} format={format}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to generate export.")

    # RFC 5987 filename encoding so non-ASCII names survive.
    ascii_name = filename.encode("ascii", "ignore").decode() or "export"
    disposition = f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": disposition},
    )
