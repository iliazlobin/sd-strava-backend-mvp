"""Effort service — record segment efforts and query leaderboards."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from strava.models.activity import Activity
from strava.models.segment import Segment
from strava.models.segment_effort import SegmentEffort
from strava.schemas.effort import EffortCreate, EffortResponse


async def create_effort(session: AsyncSession, payload: EffortCreate) -> EffortResponse:
    """Record a segment effort.

    Validates activity and segment exist (404 if not).
    Handles duplicate (activity_id, segment_id) → 409.
    Increments total_efforts on the segment atomically.
    """
    # Verify activity exists
    result = await session.execute(
        select(Activity).where(Activity.activity_id == payload.activity_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Verify segment exists
    result = await session.execute(select(Segment).where(Segment.segment_id == payload.segment_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Segment not found")

    effort = SegmentEffort(
        activity_id=payload.activity_id,
        segment_id=payload.segment_id,
        user_id=payload.user_id,
        elapsed_time=payload.elapsed_time,
    )
    session.add(effort)

    try:
        # Increment total_efforts on the segment
        await session.execute(
            update(Segment)
            .where(Segment.segment_id == payload.segment_id)
            .values(total_efforts=Segment.total_efforts + 1)
        )
        await session.flush()
        await session.refresh(effort)
        await session.commit()
        return EffortResponse.model_validate(effort)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Effort already exists for this activity and segment",
        ) from e


async def get_leaderboard(session: AsyncSession, segment_id: UUID, limit: int) -> list[dict]:
    """Get the top-N leaderboard for a segment, ordered by elapsed_time ASC.

    Tiebreaker: created_at ASC (earliest effort = higher rank).
    Rank is 1-based sequential.
    Returns 404 if segment does not exist.
    """
    from strava.services.segment_service import get_segment

    # Verify segment exists (get_segment raises 404 if not)
    await get_segment(session, segment_id)

    result = await session.execute(
        select(SegmentEffort)
        .where(SegmentEffort.segment_id == segment_id)
        .order_by(SegmentEffort.elapsed_time.asc(), SegmentEffort.created_at.asc())
        .limit(limit)
    )
    efforts = result.scalars().all()

    leaderboard = []
    for rank, effort in enumerate(efforts, start=1):
        leaderboard.append(
            {
                "rank": rank,
                "user_id": str(effort.user_id),
                "activity_id": str(effort.activity_id),
                "elapsed_time": effort.elapsed_time,
            }
        )
    return leaderboard
