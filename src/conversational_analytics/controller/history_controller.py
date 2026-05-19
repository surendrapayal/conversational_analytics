import logging
from fastapi import APIRouter, HTTPException, Query
from conversational_analytics.controller.history_service import get_session_list, get_session_detail

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sessions", tags=["History"])


@router.get("")
async def list_sessions(
    user_id: str | None = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
):
    """
    Returns paginated list of sessions ordered by latest activity descending.
    Optionally filter by user_id.
    """
    try:
        return await get_session_list(user_id=user_id, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Failed to fetch session list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
):
    """
    Returns paginated conversations within a session ordered by latest first.
    """
    try:
        result = await get_session_detail(session_id=session_id, page=page, page_size=page_size)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch session detail for session_id={session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
