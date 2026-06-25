"""FR-8: Health check endpoint.

AC-8: GET /healthz → 200 {"status":"ok"} with DB connectivity check.
"""

from verify.acceptance.conftest import assert_json_200


def test_healthz_returns_ok(client):
    """GET /healthz → 200 with status 'ok'."""
    body = assert_json_200(client.get("/healthz"))
    assert body == {"status": "ok"}


def test_healthz_returns_json(client):
    """GET /healthz → 200 with JSON content-type."""
    r = client.get("/healthz")
    assert r.status_code == 200
    assert "application/json" in r.headers.get("content-type", "")
    data = r.json()
    assert data["status"] == "ok"
