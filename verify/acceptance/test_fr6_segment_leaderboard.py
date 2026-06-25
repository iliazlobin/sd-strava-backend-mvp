"""FR-6: Get segment leaderboard — top N efforts ranked by time.

AC-6: GET /segments/{id}/leaderboard?limit=10 → 200 + array sorted by elapsed_time ASC.
Each entry has rank, user_id, activity_id, elapsed_time.
Missing segment → 404. Leaderboard respects tiebreaker (earliest effort = higher rank).
"""

from verify.acceptance.conftest import assert_201, assert_404, assert_json_200


def _create_user(client, name="Runner"):
    return assert_201(client.post("/users", json={"display_name": name}))


def _create_activity(client, user_id: str, start_time="2025-06-25T08:00:00Z"):
    return assert_201(
        client.post(
            "/activities",
            json={
                "user_id": user_id,
                "sport_type": "run",
                "start_time": start_time,
                "elapsed_time": 1800,
                "distance_m": 5000.0,
                "polyline": [[40.71, -74.00, 10.0, 1719907200]],
            },
        )
    )["activity_id"]


def _create_segment(client, name="Test Segment"):
    return assert_201(
        client.post(
            "/segments",
            json={
                "name": name,
                "polyline": [[40.71, -74.00, 5.0, 1719907200]],
                "distance_m": 1000.0,
            },
        )
    )["segment_id"]


def _record_effort(client, activity_id, segment_id, user_id, elapsed_time):
    return assert_201(
        client.post(
            "/segment-efforts",
            json={
                "activity_id": activity_id,
                "segment_id": segment_id,
                "user_id": user_id,
                "elapsed_time": elapsed_time,
            },
        )
    )


def test_leaderboard_success(client):
    """GET /segments/{id}/leaderboard → 200 with correctly ranked efforts."""
    u1 = _create_user(client, "Alice")["user_id"]
    u2 = _create_user(client, "Bob")["user_id"]
    u3 = _create_user(client, "Charlie")["user_id"]

    seg_id = _create_segment(client, "Hill Climb")

    a1 = _create_activity(client, u1)
    a2 = _create_activity(client, u2)
    a3 = _create_activity(client, u3)

    _record_effort(client, a1, seg_id, u1, 310)  # 3rd
    _record_effort(client, a2, seg_id, u2, 280)  # 1st
    _record_effort(client, a3, seg_id, u3, 305)  # 2nd

    body = assert_json_200(client.get(f"/segments/{seg_id}/leaderboard?limit=10"))
    assert isinstance(body, list)
    assert len(body) == 3

    assert body[0]["rank"] == 1
    assert body[0]["elapsed_time"] == 280
    assert body[0]["user_id"] == u2

    assert body[1]["rank"] == 2
    assert body[1]["elapsed_time"] == 305
    assert body[1]["user_id"] == u3

    assert body[2]["rank"] == 3
    assert body[2]["elapsed_time"] == 310
    assert body[2]["user_id"] == u1


def test_leaderboard_tiebreaker(client):
    """Tied times → earlier effort_id gets higher rank."""
    u1 = _create_user(client, "Alice")["user_id"]
    u2 = _create_user(client, "Bob")["user_id"]

    seg_id = _create_segment(client, "Sprint")

    a1 = _create_activity(client, u1)
    a2 = _create_activity(client, u2)

    # Alice's effort created first → should rank higher on tie
    _record_effort(client, a1, seg_id, u1, 300)
    _record_effort(client, a2, seg_id, u2, 300)

    body = assert_json_200(client.get(f"/segments/{seg_id}/leaderboard?limit=10"))
    assert len(body) == 2
    assert body[0]["rank"] == 1
    assert body[0]["user_id"] == u1  # earlier effort wins tie
    assert body[1]["rank"] == 2
    assert body[1]["user_id"] == u2


def test_leaderboard_limit(client):
    """GET leaderboard with limit=N → returns at most N efforts."""
    seg_id = _create_segment(client, "Crowded Climb")
    for i in range(5):
        u = _create_user(client, f"Runner{i}")["user_id"]
        a = _create_activity(client, u)
        _record_effort(client, a, seg_id, u, 300 + i * 10)

    body = assert_json_200(client.get(f"/segments/{seg_id}/leaderboard?limit=3"))
    assert len(body) == 3


def test_leaderboard_empty_segment(client):
    """GET leaderboard for segment with no efforts → 200 []."""
    seg_id = _create_segment(client, "Empty Segment")
    body = assert_json_200(client.get(f"/segments/{seg_id}/leaderboard?limit=10"))
    assert body == []


def test_leaderboard_missing_segment_404(client):
    """GET /segments/{id}/leaderboard with non-existent segment → 404."""
    assert_404(client.get("/segments/00000000-0000-0000-0000-000000000000/leaderboard?limit=10"))
