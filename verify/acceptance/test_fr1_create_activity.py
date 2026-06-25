"""FR-1: Create an activity with sport type, GPS polyline, and metadata.

AC-1: POST /activities with valid payload → 201 {activity_id}.
Missing required field (sport_type) → 422.
Non-existent user_id → 404.
"""

from verify.acceptance.conftest import assert_201, assert_404, assert_422

VALID_PAYLOAD = {
    "user_id": None,  # filled per test
    "sport_type": "run",
    "start_time": "2025-06-25T08:00:00Z",
    "elapsed_time": 1800,
    "distance_m": 5000.0,
    "elevation_gain_m": 50.0,
    "polyline": [
        [40.7128, -74.0060, 10.0, 1719907200],
        [40.7130, -74.0055, 12.0, 1719907260],
        [40.7135, -74.0048, 15.0, 1719907320],
    ],
    "visibility": "everyone",
}


def test_create_activity_success(client, user_ids):
    """POST /activities with valid payload → 201 with activity_id."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0]}
    body = assert_201(client.post("/activities", json=payload))
    assert "activity_id" in body
    assert isinstance(body["activity_id"], str) and len(body["activity_id"]) > 0


def test_create_activity_minimal_fields(client, user_ids):
    """POST /activities with only required fields (no elevation_gain_m, no visibility) → 201."""
    payload = {
        "user_id": user_ids[0],
        "sport_type": "ride",
        "start_time": "2025-06-25T09:00:00Z",
        "elapsed_time": 3600,
        "distance_m": 25000.0,
        "polyline": [[40.71, -74.00, 5.0, 1719907200]],
    }
    body = assert_201(client.post("/activities", json=payload))
    assert "activity_id" in body


def test_create_activity_missing_sport_type_422(client, user_ids):
    """POST /activities without sport_type → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0]}
    del payload["sport_type"]
    assert_422(client.post("/activities", json=payload))


def test_create_activity_missing_polyline_422(client, user_ids):
    """POST /activities without polyline → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0]}
    del payload["polyline"]
    assert_422(client.post("/activities", json=payload))


def test_create_activity_missing_user_id_422(client):
    """POST /activities without user_id → 422."""
    payload = {**VALID_PAYLOAD}  # user_id is None, will be dropped
    del payload["user_id"]
    assert_422(client.post("/activities", json=payload))


def test_create_activity_nonexistent_user_404(client):
    """POST /activities with non-existent user_id → 404."""
    payload = {**VALID_PAYLOAD, "user_id": "00000000-0000-0000-0000-000000000000"}
    assert_404(client.post("/activities", json=payload))


def test_create_activity_empty_polyline_422(client, user_ids):
    """POST /activities with empty polyline array → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0], "polyline": []}
    assert_422(client.post("/activities", json=payload))


def test_create_activity_invalid_sport_type_422(client, user_ids):
    """POST /activities with invalid sport_type → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0], "sport_type": "flying"}
    assert_422(client.post("/activities", json=payload))


def test_create_activity_negative_distance_422(client, user_ids):
    """POST /activities with negative distance_m → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0], "distance_m": -1.0}
    assert_422(client.post("/activities", json=payload))


def test_create_activity_zero_elapsed_time_422(client, user_ids):
    """POST /activities with elapsed_time = 0 → 422."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0], "elapsed_time": 0}
    assert_422(client.post("/activities", json=payload))
