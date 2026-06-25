"""User service — create and query user entities."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from strava.models.user import User
from strava.schemas.user import UserResponse


async def create_user(session: AsyncSession, display_name: str) -> UserResponse:
    """Create a new user and return the full UserResponse."""
    user = User(display_name=display_name)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return UserResponse.model_validate(user)


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    """Fetch a user by ID or return None."""
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()
