"""Tests for SQLAlchemy ORM model classes — structure and instantiation.

SQLAlchemy column defaults (server_default, default with callables like uuid.uuid4)
are applied at INSERT time, not at Python instantiation. These tests verify that
the models have the correct structure and can be instantiated with explicit values.
"""

import uuid

import pytest

from strava.models import Activity, Kudos, Segment, SegmentEffort, User


@pytest.mark.asyncio
async def test_user_model_attributes() -> None:
    """User model has the expected column attributes."""
    uid = uuid.uuid4()
    user = User(user_id=uid, display_name="Alice")
    assert user.user_id == uid
    assert user.display_name == "Alice"
    assert hasattr(user, "created_at")


@pytest.mark.asyncio
async def test_user_table_name() -> None:
    """User model maps to the 'users' table."""
    assert User.__tablename__ == "users"


@pytest.mark.asyncio
async def test_activity_model_attributes() -> None:
    """Activity model has all expected columns and accepts values."""
    uid = uuid.uuid4()
    activity = Activity(
        activity_id=uid,
        user_id=uuid.uuid4(),
        sport_type="run",
        start_time=__import__("datetime").datetime.now(),
        elapsed_time=1800,
        distance_m=5000.0,
        polyline=[[40.7128, -74.0060, 10.0, 1719907200]],
        visibility="everyone",
        kudos_count=0,
        elevation_gain_m=0.0,
    )
    assert activity.activity_id == uid
    assert activity.sport_type == "run"
    assert activity.elapsed_time == 1800
    assert activity.distance_m == 5000.0
    assert activity.visibility == "everyone"
    assert activity.kudos_count == 0
    assert activity.elevation_gain_m == 0.0


@pytest.mark.asyncio
async def test_activity_table_name() -> None:
    """Activity model maps to the 'activities' table."""
    assert Activity.__tablename__ == "activities"


@pytest.mark.asyncio
async def test_segment_model_attributes() -> None:
    """Segment model has all expected columns and accepts values."""
    uid = uuid.uuid4()
    segment = Segment(
        segment_id=uid,
        name="Baker Street Hill Climb",
        polyline=[[40.71, -74.00, 5.0, 1719907200]],
        distance_m=1200.0,
        total_efforts=0,
    )
    assert segment.segment_id == uid
    assert segment.name == "Baker Street Hill Climb"
    assert segment.distance_m == 1200.0
    assert segment.total_efforts == 0


@pytest.mark.asyncio
async def test_segment_table_name() -> None:
    """Segment model maps to the 'segments' table."""
    assert Segment.__tablename__ == "segments"


@pytest.mark.asyncio
async def test_segment_effort_model_attributes() -> None:
    """SegmentEffort model has all expected columns and accepts values."""
    uid = uuid.uuid4()
    effort = SegmentEffort(
        effort_id=uid,
        segment_id=uuid.uuid4(),
        activity_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        elapsed_time=305,
    )
    assert effort.effort_id == uid
    assert effort.elapsed_time == 305
    assert effort.segment_id is not None
    assert effort.activity_id is not None


@pytest.mark.asyncio
async def test_segment_effort_table_name() -> None:
    """SegmentEffort model maps to the 'segment_efforts' table."""
    assert SegmentEffort.__tablename__ == "segment_efforts"


@pytest.mark.asyncio
async def test_kudos_model_attributes() -> None:
    """Kudos model has composite PK of (activity_id, user_id)."""
    aid = uuid.uuid4()
    uid = uuid.uuid4()
    kudos = Kudos(activity_id=aid, user_id=uid)
    assert kudos.activity_id == aid
    assert kudos.user_id == uid
    assert hasattr(kudos, "created_at")


@pytest.mark.asyncio
async def test_kudos_table_name() -> None:
    """Kudos model maps to the 'kudos' table."""
    assert Kudos.__tablename__ == "kudos"


@pytest.mark.asyncio
async def test_all_models_are_orm_classes() -> None:
    """All five models inherit from the SQLAlchemy DeclarativeBase."""
    from sqlalchemy.orm import DeclarativeBase

    assert issubclass(User, DeclarativeBase)
    assert issubclass(Activity, DeclarativeBase)
    assert issubclass(Segment, DeclarativeBase)
    assert issubclass(SegmentEffort, DeclarativeBase)
    assert issubclass(Kudos, DeclarativeBase)
