"""POST /segments, GET /segments/{segment_id} — create and retrieve segments."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.schemas.segment import SegmentCreate, SegmentResponse
from strava.services import segment_service

router = APIRouter()


@router.post("", status_code=201)
async def create_segment(
    payload: SegmentCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new segment. Returns 201 with segment_id."""
    segment_id = await segment_service.create_segment(session, payload)
    return {"segment_id": str(segment_id)}


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> SegmentResponse:
    """Get segment detail by ID. Returns 404 if not found."""
    return await segment_service.get_segment(session, segment_id)
