"""User request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Request body for POST /users."""

    display_name: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Response body for POST /users."""

    user_id: UUID
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
