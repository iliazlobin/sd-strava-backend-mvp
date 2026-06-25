"""FR-3: List user activities (paginated, reverse-chronological).

AC-3: GET /users/{id}/activities?limit=10&offset=0 → 200 + array (newest first).
User with no activities → 200 + [].
Non-existent user → 404.
"""

from verify.acceptance.conftest import assert_201, assert_404, assert_json_200


def test_list_activities_success(client, user_ids):
    """GET /users/{id}/activities → 200 with activities ordered newest-first."""
    u1 = user_ids[0]
    # Create two activities for u1
    payloads = [
        {
            "user_id": u1,
            "sport_type": "run",
            "start_time": "2025-06-25T08:00:00Z",
            "elapsed_time": 1800,
            "distance_m": 5000.0,
            "polyline": [[40.71, -74.00, 10.0, 1719907200]],
        },
        {
            "user_id": u1,
            "sport_type": "ride",
            "start_time": "2025-06-25T10:00:00Z",
            "elapsed_time": 3600,
            "distance_m": 25000.0,
            "polyline": [[40.72, -74.01, 15.0, 1719914400]],
        },
    ]
    ids = []
    for p in payloads:
        body = assert_201(client.post("/activities", json=p))
        ids.append(body["activity_id"])

    body = assert_json_200(client.get(f"/users/{u1}/activities?limit=10&offset=0"))
    assert isinstance(body, list)
    assert len(body) == 2
    # Newest first: the second activity created should be first
    assert body[0]["activity_id"] == ids[1]
    assert body[1]["activity_id"] == ids[0]


def test_list_activities_pagination(client, user_ids):
    """GET /users/{id}/activities with limit respects the page size."""
    u1 = user_ids[0]
    for i in range(5):
        p = {
            "user_id": u1,
            "sport_type": "walk",
            "start_time": f"2025-06-25T0{i}:00:00Z",
            "elapsed_time": 600,
            "distance_m": 1000.0,
            "polyline": [[40.71, -74.00, 5.0, 1719907200]],
        }
        assert_201(client.post("/activities", json=p))

    # Fetch limit=2
    body = assert_json_200(client.get(f"/users/{u1}/activities?limit=2&offset=0"))
    assert len(body) == 2

    # Fetch offset=2
    body = assert_json_200(client.get(f"/users/{u1}/activities?limit=10&offset=2"))
    assert len(body) == 3


def test_list_activities_empty_user(client, user_ids):
    """GET /users/{id}/activities for user with no activities → 200 []."""
    # user_ids[2] has no activities created
    body = assert_json_200(client.get(f"/users/{user_ids[2]}/activities?limit=10&offset=0"))
    assert body == []


def test_list_activities_nonexistent_user_404(client):
    """GET /users/{id}/activities with non-existent user → 404."""
    assert_404(
        client.get("/users/00000000-0000-0000-0000-000000000000/activities?limit=10&offset=0")
    )
