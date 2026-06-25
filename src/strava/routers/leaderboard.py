"""GET /segments/{segment_id}/leaderboard — top-N ranked efforts by time."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.services import effort_service

router = APIRouter()


@router.get("/{segment_id}/leaderboard")
async def get_leaderboard(
    segment_id: UUID,
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get the top-N leaderboard for a segment, ranked by elapsed_time ASC."""
    return await effort_service.get_leaderboard(session, segment_id, limit)
