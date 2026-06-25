"""Pydantic schemas for the Strava MVP API."""

from strava.schemas.user import UserCreate, UserResponse
from strava.schemas.activity import ActivityCreate, ActivityResponse
from strava.schemas.segment import SegmentCreate, SegmentResponse
from strava.schemas.effort import EffortCreate, EffortResponse
from strava.schemas.kudos import KudosRequest, KudosResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "ActivityCreate",
    "ActivityResponse",
    "SegmentCreate",
    "SegmentResponse",
    "EffortCreate",
    "EffortResponse",
    "KudosRequest",
    "KudosResponse",
]
