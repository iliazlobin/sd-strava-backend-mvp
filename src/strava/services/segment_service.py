"""Segment service — create and retrieve segments."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from strava.models.segment import Segment
from strava.schemas.segment import SegmentCreate, SegmentResponse


async def create_segment(
    session: AsyncSession, payload: SegmentCreate
) -> UUID:
    """Create a new segment. Returns the segment_id."""
    segment = Segment(
        name=payload.name,
        polyline=payload.polyline,
        distance_m=payload.distance_m,
    )
    session.add(segment)
    await session.flush()
    await session.commit()
    return segment.segment_id


async def get_segment(
    session: AsyncSession, segment_id: UUID
) -> SegmentResponse:
    """Fetch a segment by ID. Raises 404 if not found."""
    result = await session.execute(
        select(Segment).where(Segment.segment_id == segment_id)
    )
    segment = result.scalar_one_or_none()
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentResponse.model_validate(segment)
