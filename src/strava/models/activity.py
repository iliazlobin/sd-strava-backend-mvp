"""Activity model — an athletic activity with GPS track."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Double,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from strava.database import Base


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint(
            "sport_type IN ('run','ride','swim','hike','walk','other')",
            name="ck_activities_sport_type",
        ),
        CheckConstraint("elapsed_time > 0", name="ck_activities_elapsed_time"),
        CheckConstraint("distance_m >= 0", name="ck_activities_distance_m"),
        CheckConstraint("elevation_gain_m >= 0", name="ck_activities_elevation_gain_m"),
        CheckConstraint(
            "visibility IN ('everyone','followers','only_me')",
            name="ck_activities_visibility",
        ),
    )

    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )
    sport_type: Mapped[str] = mapped_column(String(10), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    elapsed_time: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_m: Mapped[float] = mapped_column(Double, nullable=False)
    elevation_gain_m: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    polyline: Mapped[object] = mapped_column(JSONB, nullable=False)
    visibility: Mapped[str] = mapped_column(String(10), nullable=False, default="everyone")
    kudos_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
