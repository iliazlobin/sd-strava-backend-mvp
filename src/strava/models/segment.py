"""Segment model — a named route section for competition."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Double, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from strava.database import Base


class Segment(Base):
    __tablename__ = "segments"
    __table_args__ = (
        CheckConstraint("distance_m >= 0", name="ck_segments_distance_m"),
    )

    segment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    polyline: Mapped[object] = mapped_column(JSONB, nullable=False)
    distance_m: Mapped[float] = mapped_column(Double, nullable=False)
    total_efforts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
