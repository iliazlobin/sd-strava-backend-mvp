"""Kudos request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class KudosRequest(BaseModel):
    """Request body for POST /activities/{id}/kudos."""

    user_id: UUID


class KudosResponse(BaseModel):
    """Response body for POST /activities/{id}/kudos."""

    status: str


class KudosListEntry(BaseModel):
    """Entry in the kudos list response."""

    user_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
