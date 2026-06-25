"""Kudos service — give kudos (idempotent) and list kudos."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from strava.models.activity import Activity
from strava.models.kudos import Kudos
from strava.schemas.kudos import KudosListEntry


async def give_kudos(session: AsyncSession, activity_id: UUID, user_id: UUID) -> tuple[str, int]:
    """Give kudos to an activity.

    Returns (status, http_status_code):
      - ("created", 201) — first time this user kudos'd this activity
      - ("already_exists", 200) — idempotent: user already gave kudos

    Raises 404 if activity does not exist.
    Idempotency is enforced by the PRIMARY KEY (activity_id, user_id).
    kudos_count is incremented only on first kudos.
    """
    # Verify activity exists
    result = await session.execute(select(Activity).where(Activity.activity_id == activity_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Try to insert; ON CONFLICT DO NOTHING for idempotency
    result = await session.execute(
        text("""
            INSERT INTO kudos (activity_id, user_id)
            VALUES (:activity_id, :user_id)
            ON CONFLICT (activity_id, user_id) DO NOTHING
            RETURNING activity_id
        """),
        {"activity_id": activity_id, "user_id": user_id},
    )
    row = result.fetchone()

    if row is not None:
        # First kudos — increment the counter
        await session.execute(
            update(Activity)
            .where(Activity.activity_id == activity_id)
            .values(kudos_count=Activity.kudos_count + 1)
        )
        await session.commit()
        return "created", 201
    else:
        await session.commit()
        return "already_exists", 200


async def list_kudos(session: AsyncSession, activity_id: UUID) -> list[KudosListEntry]:
    """List all kudos for an activity, oldest first.

    Raises 404 if activity does not exist.
    """
    # Verify activity exists
    result = await session.execute(select(Activity).where(Activity.activity_id == activity_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    result = await session.execute(
        select(Kudos).where(Kudos.activity_id == activity_id).order_by(Kudos.created_at.asc())
    )
    kudos_list = result.scalars().all()
    return [KudosListEntry.model_validate(k) for k in kudos_list]
