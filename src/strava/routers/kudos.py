"""POST /activities/{activity_id}/kudos, GET /activities/{activity_id}/kudos — give and list kudos."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.schemas.kudos import KudosRequest, KudosResponse, KudosListEntry
from strava.services import kudos_service

router = APIRouter()


@router.post("/{activity_id}/kudos")
async def give_kudos(
    activity_id: UUID,
    payload: KudosRequest,
    session: AsyncSession = Depends(get_db),
):
    """Give kudos to an activity. Idempotent: 201 first time, 200 thereafter."""
    status, http_code = await kudos_service.give_kudos(
        session, activity_id, payload.user_id
    )
    return Response(
        status_code=http_code,
        content=KudosResponse(status=status).model_dump_json(),
        media_type="application/json",
    )


@router.get("/{activity_id}/kudos", response_model=list[KudosListEntry])
async def list_kudos(
    activity_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> list[KudosListEntry]:
    """List all kudos for an activity, oldest first. Returns 404 if activity not found."""
    return await kudos_service.list_kudos(session, activity_id)
