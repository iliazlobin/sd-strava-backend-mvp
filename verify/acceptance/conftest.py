"""Shared fixtures and helpers for the black-box acceptance suite.

These tests do NOT import `src.strava`. They talk to the running system
via HTTP at API_BASE_URL.
"""

import os

import httpx
import pytest

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def base_url():
    return API_BASE_URL


@pytest.fixture(scope="session")
def client(base_url):
    """Session-scoped synchronous httpx client for the entire acceptance run."""
    with httpx.Client(base_url=base_url, timeout=10) as c:
        yield c


@pytest.fixture
def user_ids(client):
    """Create three fresh test users and return their UUIDs."""
    ids = []
    for name in ("Alice", "Bob", "Charlie"):
        r = client.post("/users", json={"display_name": name})
        assert r.status_code == 201, f"Failed to create user {name}: {r.text}"
        ids.append(r.json()["user_id"])
    return ids


# --- Helper assertions ---


def assert_json_200(r, expected_status=200):
    """Assert status and return parsed JSON."""
    assert (
        r.status_code == expected_status
    ), f"Expected {expected_status}, got {r.status_code}: {r.text}"
    return r.json()


def assert_201(r):
    return assert_json_200(r, 201)


def assert_422(r):
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    return r.json()


def assert_404(r):
    assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"
    return r.json()


def assert_409(r):
    assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"
    return r.json()
