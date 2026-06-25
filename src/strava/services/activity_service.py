"""Activity service — create, retrieve, and list activities."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from strava.models.activity import Activity
from strava.schemas.activity import ActivityCreate, ActivityResponse


async def create_activity(
    session: AsyncSession, payload: ActivityCreate
) -> UUID:
    """Create a new activity. Returns the activity_id.

    Validates that the referenced user exists (404 if not).
    """
    from strava.services.user_service import get_user_by_id

    user = await get_user_by_id(session, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    activity = Activity(
        user_id=payload.user_id,
        sport_type=payload.sport_type,
        start_time=payload.start_time,
        elapsed_time=payload.elapsed_time,
        distance_m=payload.distance_m,
        elevation_gain_m=payload.elevation_gain_m,
        polyline=payload.polyline,
        visibility=payload.visibility,
    )
    session.add(activity)
    await session.flush()
    await session.commit()
    return activity.activity_id


async def get_activity(
    session: AsyncSession, activity_id: UUID
) -> ActivityResponse:
    """Fetch a full activity by ID. Raises 404 if not found."""
    result = await session.execute(
        select(Activity).where(Activity.activity_id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityResponse.model_validate(activity)


async def list_activities(
    session: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[ActivityResponse]:
    """List activities for a user, newest first. Raises 404 if user not found."""
    from strava.services.user_service import get_user_by_id

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await session.execute(
        select(Activity)
        .where(Activity.user_id == user_id)
        .order_by(Activity.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    activities = result.scalars().all()
    return [ActivityResponse.model_validate(a) for a in activities]
