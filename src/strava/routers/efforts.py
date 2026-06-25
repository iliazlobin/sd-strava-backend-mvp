"""POST /segment-efforts — record a segment effort."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.schemas.effort import EffortCreate, EffortResponse
from strava.services import effort_service

router = APIRouter()


@router.post("", status_code=201, response_model=EffortResponse)
async def create_effort(
    payload: EffortCreate,
    session: AsyncSession = Depends(get_db),
) -> EffortResponse:
    """Record a segment effort. Returns 201, or 409 on duplicate."""
    return await effort_service.create_effort(session, payload)
