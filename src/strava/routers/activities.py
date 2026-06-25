"""POST /activities, GET /activities/{activity_id} — create and retrieve activities."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.schemas.activity import ActivityCreate, ActivityResponse
from strava.services import activity_service

router = APIRouter()


@router.post("", status_code=201)
async def create_activity(
    payload: ActivityCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new activity. Returns 201 with activity_id."""
    activity_id = await activity_service.create_activity(session, payload)
    return {"activity_id": str(activity_id)}


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    """Get activity detail by ID. Returns 404 if not found."""
    return await activity_service.get_activity(session, activity_id)
