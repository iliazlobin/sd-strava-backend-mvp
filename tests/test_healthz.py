"""Tests for the healthz endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthz_returns_200(client: AsyncClient) -> None:
    """GET /healthz returns 200 OK when DB is healthy."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok"}


@pytest.mark.asyncio
async def test_healthz_response_is_json(client: AsyncClient) -> None:
    """Healthz returns valid JSON with expected keys."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert "status" in response.json()
