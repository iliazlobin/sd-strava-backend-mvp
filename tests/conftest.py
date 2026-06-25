"""Test fixtures for Strava MVP unit tests."""

import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def isolated_settings() -> Generator[None, None, None]:
    """Isolate settings from real .env during tests."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///file::memory:")
    yield


@pytest_asyncio.fixture(loop_scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Return an httpx AsyncClient bound to the FastAPI app with mocked DB."""
    with patch("strava.main.check_db_health", new_callable=AsyncMock) as mock_check, \
         patch("strava.main.init_db", new_callable=AsyncMock), \
         patch("strava.main.dispose_db", new_callable=AsyncMock):
        mock_check.return_value = True
        app = __import__("strava.main", fromlist=["create_app"]).create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
