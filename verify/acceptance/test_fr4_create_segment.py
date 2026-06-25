"""FR-4: Create a segment with a name and bounding polyline.

AC-4: POST /segments with valid payload → 201 {segment_id}.
Missing name → 422.
"""

from verify.acceptance.conftest import assert_201, assert_422


VALID_SEGMENT = {
    "name": "Baker Street Hill Climb",
    "polyline": [
        [40.7128, -74.0060, 5.0, 1719907200],
        [40.7135, -74.0048, 15.0, 1719907260],
        [40.7142, -74.0035, 25.0, 1719907320],
    ],
    "distance_m": 1200.0,
}


def test_create_segment_success(client):
    """POST /segments with valid payload → 201 with segment_id."""
    body = assert_201(client.post("/segments", json=VALID_SEGMENT))
    assert "segment_id" in body
    assert isinstance(body["segment_id"], str) and len(body["segment_id"]) > 0


def test_create_segment_minimal(client):
    """POST /segments with min distance_m=0 → 201 (e.g., flat segment)."""
    payload = {
        "name": "Flat Sprint",
        "polyline": [[40.71, -74.00, 5.0, 1719907200]],
        "distance_m": 0.0,
    }
    body = assert_201(client.post("/segments", json=payload))
    assert "segment_id" in body


def test_create_segment_missing_name_422(client):
    """POST /segments without name → 422."""
    payload = {**VALID_SEGMENT}
    del payload["name"]
    assert_422(client.post("/segments", json=payload))


def test_create_segment_missing_polyline_422(client):
    """POST /segments without polyline → 422."""
    payload = {**VALID_SEGMENT}
    del payload["polyline"]
    assert_422(client.post("/segments", json=payload))


def test_create_segment_missing_distance_422(client):
    """POST /segments without distance_m → 422."""
    payload = {**VALID_SEGMENT}
    del payload["distance_m"]
    assert_422(client.post("/segments", json=payload))


def test_create_segment_empty_polyline_422(client):
    """POST /segments with empty polyline → 422."""
    payload = {**VALID_SEGMENT, "polyline": []}
    assert_422(client.post("/segments", json=payload))


def test_create_segment_negative_distance_422(client):
    """POST /segments with negative distance_m → 422."""
    payload = {**VALID_SEGMENT, "distance_m": -1.0}
    assert_422(client.post("/segments", json=payload))
