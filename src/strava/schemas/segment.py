"""Segment request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SegmentCreate(BaseModel):
    """Request body for POST /segments."""

    name: str = Field(..., min_length=1)
    polyline: list[list[float]] = Field(..., min_length=1)
    distance_m: float = Field(..., ge=0)


class SegmentResponse(BaseModel):
    """Response body for GET /segments/{id}."""

    segment_id: UUID
    name: str
    polyline: list[list[float]]
    distance_m: float
    total_efforts: int
    created_at: datetime

    model_config = {"from_attributes": True}
