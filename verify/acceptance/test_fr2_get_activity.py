"""FR-2: Get activity detail by ID including full GPS polyline.

AC-2: GET /activities/{id} → 200 + full activity JSON.
Non-existent ID → 404.
"""

from verify.acceptance.conftest import assert_json_200, assert_404, assert_201


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
    ],
    "visibility": "everyone",
}


def test_get_activity_success(client, user_ids):
    """GET /activities/{id} → 200 with full activity data."""
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0]}
    created = assert_201(client.post("/activities", json=payload))
    activity_id = created["activity_id"]

    body = assert_json_200(client.get(f"/activities/{activity_id}"))
    assert body["activity_id"] == activity_id
    assert body["user_id"] == user_ids[0]
    assert body["sport_type"] == "run"
    assert body["start_time"] == "2025-06-25T08:00:00Z"
    assert body["elapsed_time"] == 1800
    assert body["distance_m"] == 5000.0
    assert body["elevation_gain_m"] == 50.0
    assert body["polyline"] == VALID_PAYLOAD["polyline"]
    assert body["visibility"] == "everyone"
    assert "kudos_count" in body
    assert body["kudos_count"] == 0
    assert "created_at" in body


def test_get_activity_not_found_404(client):
    """GET /activities/{id} with non-existent UUID → 404."""
    assert_404(client.get("/activities/00000000-0000-0000-0000-000000000000"))


def test_get_activity_returns_polyline(client, user_ids):
    """GET /activities/{id} — polyline is returned exactly as submitted."""
    poly = [[40.71, -74.00, 5.5, 1719907200], [40.72, -74.01, 25.0, 1719907300]]
    payload = {**VALID_PAYLOAD, "user_id": user_ids[0], "polyline": poly}
    created = assert_201(client.post("/activities", json=payload))
    body = assert_json_200(client.get(f"/activities/{created['activity_id']}"))
    assert body["polyline"] == poly
