"""Database engine, session factory, and FastAPI dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from strava.config import Settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


_engine = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _get_engine(database_url: str | None = None):
    """Return the async engine, creating it lazily on first call."""
    global _engine
    if _engine is None:
        url = database_url or Settings().database_url
        _engine = create_async_engine(url, echo=False)
    return _engine


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return the session factory."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Services commit explicitly. This dependency provides the session
    and ensures cleanup.
    """
    session = _get_sessionmaker()()
    try:
        yield session
    finally:
        await session.close()


async def init_db(database_url: str | None = None) -> None:
    """Initialise the database engine. Called during app lifespan startup."""
    _get_engine(database_url)


async def dispose_db() -> None:
    """Dispose the database engine. Called during app lifespan shutdown."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None


async def check_db_health() -> bool:
    """Check database connectivity with a simple SELECT 1."""
    from sqlalchemy import text

    try:
        async with _get_sessionmaker()() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
