"""FR-7: Give kudos on activities (idempotent) and list kudos.

AC-7: POST /activities/{id}/kudos → 201 (first time). Same user+activity again → 200.
Missing activity → 404. GET /activities/{id}/kudos → 200 + list.
"""

from verify.acceptance.conftest import assert_json_200, assert_404, assert_422, assert_201


def _create_user(client, name="Runner"):
    return assert_201(client.post("/users", json={"display_name": name}))


def _create_activity(client, user_id):
    return assert_201(client.post("/activities", json={
        "user_id": user_id,
        "sport_type": "run",
        "start_time": "2025-06-25T08:00:00Z",
        "elapsed_time": 1800,
        "distance_m": 5000.0,
        "polyline": [[40.71, -74.00, 10.0, 1719907200]],
    }))["activity_id"]


def test_give_kudos_first_time_201(client):
    """POST /activities/{id}/kudos first time → 201."""
    u = _create_user(client, "Alice")
    activity_id = _create_activity(client, u["user_id"])

    # Another user gives kudos
    u2 = _create_user(client, "Bob")
    r = client.post(f"/activities/{activity_id}/kudos", json={"user_id": u2["user_id"]})
    assert r.status_code == 201
    body = r.json()
    assert body.get("status") == "created"


def test_give_kudos_idempotent_200(client):
    """POST /activities/{id}/kudos same user+activity → 200 (idempotent)."""
    u = _create_user(client, "Alice")
    activity_id = _create_activity(client, u["user_id"])
    u2 = _create_user(client, "Bob")["user_id"]

    # First kudos → 201
    r1 = client.post(f"/activities/{activity_id}/kudos", json={"user_id": u2})
    assert r1.status_code == 201

    # Second kudos same user+activity → 200
    r2 = client.post(f"/activities/{activity_id}/kudos", json={"user_id": u2})
    assert r2.status_code == 200
    body = r2.json()
    assert body.get("status") == "already_exists"


def test_give_kudos_multiple_users(client):
    """Different users can kudos the same activity → each gets 201 on first attempt."""
    owner = _create_user(client, "Owner")
    activity_id = _create_activity(client, owner["user_id"])

    for name in ("Alice", "Bob", "Charlie"):
        u = _create_user(client, name)
        r = client.post(f"/activities/{activity_id}/kudos", json={"user_id": u["user_id"]})
        assert r.status_code == 201, f"{name}'s kudos should be 201"


def test_give_kudos_missing_activity_404(client):
    """POST /activities/{id}/kudos with non-existent activity → 404."""
    u = _create_user(client, "Alice")
    assert_404(client.post(
        "/activities/00000000-0000-0000-0000-000000000000/kudos",
        json={"user_id": u["user_id"]},
    ))


def test_give_kudos_missing_user_id_422(client):
    """POST /activities/{id}/kudos without user_id → 422."""
    owner = _create_user(client, "Owner")
    activity_id = _create_activity(client, owner["user_id"])
    assert_422(client.post(f"/activities/{activity_id}/kudos", json={}))


def test_list_kudos_success(client):
    """GET /activities/{id}/kudos → 200 with list of kudos."""
    owner = _create_user(client, "Owner")
    activity_id = _create_activity(client, owner["user_id"])

    u1 = _create_user(client, "Alice")
    u2 = _create_user(client, "Bob")

    client.post(f"/activities/{activity_id}/kudos", json={"user_id": u1["user_id"]})
    client.post(f"/activities/{activity_id}/kudos", json={"user_id": u2["user_id"]})

    body = assert_json_200(client.get(f"/activities/{activity_id}/kudos"))
    assert isinstance(body, list)
    assert len(body) == 2
    assert {k["user_id"] for k in body} == {u1["user_id"], u2["user_id"]}


def test_list_kudos_empty(client):
    """GET /activities/{id}/kudos with no kudos → 200 []."""
    owner = _create_user(client, "Owner")
    activity_id = _create_activity(client, owner["user_id"])
    body = assert_json_200(client.get(f"/activities/{activity_id}/kudos"))
    assert body == []


def test_list_kudos_missing_activity_404(client):
    """GET /activities/{id}/kudos with non-existent activity → 404."""
    assert_404(client.get("/activities/00000000-0000-0000-0000-000000000000/kudos"))
