"""POST /users — create a new user."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from strava.database import get_db
from strava.schemas.user import UserCreate, UserResponse
from strava.services import user_service

router = APIRouter()


@router.post("", status_code=201, response_model=UserResponse)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user with a display name."""
    return await user_service.create_user(session, payload.display_name)
