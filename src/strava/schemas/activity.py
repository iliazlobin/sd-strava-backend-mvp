"""Activity request/response schemas."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    """Request body for POST /activities."""

    user_id: UUID
    sport_type: Literal["run", "ride", "swim", "hike", "walk", "other"]
    start_time: datetime
    elapsed_time: int = Field(..., gt=0)
    distance_m: float = Field(..., ge=0)
    elevation_gain_m: float = Field(default=0.0, ge=0)
    polyline: list[list[float]] = Field(..., min_length=1)
    visibility: Literal["everyone", "followers", "only_me"] = "everyone"


class ActivityResponse(BaseModel):
    """Response body for GET /activities/{id} and list endpoints."""

    activity_id: UUID
    user_id: UUID
    sport_type: str
    start_time: datetime
    elapsed_time: int
    distance_m: float
    elevation_gain_m: float
    polyline: list[list[float]]
    visibility: str
    kudos_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
