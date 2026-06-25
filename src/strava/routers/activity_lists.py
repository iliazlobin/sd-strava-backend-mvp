"""GET /users/{user_id}/activities — paginated list of user activities."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.services import activity_service

router = APIRouter()


@router.get("/{user_id}/activities")
async def list_activities(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List activities for a user, newest first. Paginated."""
    return await activity_service.list_activities(session, user_id, limit, offset)
