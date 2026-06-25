"""FR-5: Record a segment effort with elapsed time.

AC-5: POST /segment-efforts → 201.
Duplicate (activity_id, segment_id) → 409.
Non-existent activity or segment → 404.
"""

from verify.acceptance.conftest import assert_201, assert_404, assert_409, assert_422


def _create_user(client):
    return assert_201(client.post("/users", json={"display_name": "Runner"}))


def _create_activity(client, user_id):
    return assert_201(
        client.post(
            "/activities",
            json={
                "user_id": user_id,
                "sport_type": "run",
                "start_time": "2025-06-25T08:00:00Z",
                "elapsed_time": 1800,
                "distance_m": 5000.0,
                "polyline": [[40.71, -74.00, 10.0, 1719907200]],
            },
        )
    )["activity_id"]


def _create_segment(client):
    return assert_201(
        client.post(
            "/segments",
            json={
                "name": "Test Segment",
                "polyline": [[40.71, -74.00, 5.0, 1719907200]],
                "distance_m": 1000.0,
            },
        )
    )["segment_id"]


def test_record_effort_success(client):
    """POST /segment-efforts with valid payload → 201."""
    user = _create_user(client)
    activity_id = _create_activity(client, user["user_id"])
    segment_id = _create_segment(client)

    body = assert_201(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": activity_id,
                "segment_id": segment_id,
                "user_id": user["user_id"],
                "elapsed_time": 305,
            },
        )
    )
    assert "effort_id" in body
    assert body["activity_id"] == activity_id
    assert body["segment_id"] == segment_id
    assert body["elapsed_time"] == 305


def test_record_effort_duplicate_409(client):
    """POST /segment-efforts with same (activity_id, segment_id) → 409."""
    user = _create_user(client)
    activity_id = _create_activity(client, user["user_id"])
    segment_id = _create_segment(client)

    payload = {
        "activity_id": activity_id,
        "segment_id": segment_id,
        "user_id": user["user_id"],
        "elapsed_time": 310,
    }
    assert_201(client.post("/segment-efforts", json=payload))
    # Second attempt with same activity+segment → 409
    assert_409(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": activity_id,
                "segment_id": segment_id,
                "user_id": user["user_id"],
                "elapsed_time": 320,
            },
        )
    )


def test_record_effort_nonexistent_activity_404(client):
    """POST /segment-efforts with non-existent activity_id → 404."""
    user = _create_user(client)
    segment_id = _create_segment(client)

    assert_404(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": "00000000-0000-0000-0000-000000000000",
                "segment_id": segment_id,
                "user_id": user["user_id"],
                "elapsed_time": 300,
            },
        )
    )


def test_record_effort_nonexistent_segment_404(client):
    """POST /segment-efforts with non-existent segment_id → 404."""
    user = _create_user(client)
    activity_id = _create_activity(client, user["user_id"])

    assert_404(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": activity_id,
                "segment_id": "00000000-0000-0000-0000-000000000000",
                "user_id": user["user_id"],
                "elapsed_time": 300,
            },
        )
    )


def test_record_effort_missing_required_422(client):
    """POST /segment-efforts with missing fields → 422."""
    user = _create_user(client)
    activity_id = _create_activity(client, user["user_id"])
    segment_id = _create_segment(client)

    # Missing elapsed_time
    assert_422(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": activity_id,
                "segment_id": segment_id,
                "user_id": user["user_id"],
            },
        )
    )
