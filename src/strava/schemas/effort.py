"""Effort request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EffortCreate(BaseModel):
    """Request body for POST /segment-efforts."""

    activity_id: UUID
    segment_id: UUID
    user_id: UUID
    elapsed_time: int = Field(..., gt=0)


class EffortResponse(BaseModel):
    """Response body for POST /segment-efforts."""

    effort_id: UUID
    activity_id: UUID
    segment_id: UUID
    user_id: UUID
    elapsed_time: int
    created_at: datetime

    model_config = {"from_attributes": True}
