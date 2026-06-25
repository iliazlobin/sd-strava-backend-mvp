"""FastAPI application factory with lifespan management and health check."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from strava.config import Settings
from strava.database import check_db_health, dispose_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialise DB on startup, dispose on shutdown."""
    settings = Settings()
    await init_db(settings.database_url)
    yield
    await dispose_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="Strava MVP",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Health check endpoint
    @app.get("/healthz")
    async def healthz(_request: Request) -> JSONResponse:
        db_ok = await check_db_health()
        if db_ok:
            return JSONResponse(status_code=200, content={"status": "ok"})
        return JSONResponse(
            status_code=503, content={"status": "degraded", "detail": "database unreachable"}
        )

    # Mount router stubs (all return 501 until C3 implements them)
    from strava.routers import (
        activities,
        activity_lists,
        efforts,
        kudos,
        leaderboard,
        segments,
        users,
    )

    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(activities.router, prefix="/activities", tags=["Activities"])
    app.include_router(activity_lists.router, prefix="/users", tags=["Activity Lists"])
    app.include_router(segments.router, prefix="/segments", tags=["Segments"])
    app.include_router(efforts.router, prefix="/segment-efforts", tags=["Efforts"])
    app.include_router(leaderboard.router, prefix="/segments", tags=["Leaderboard"])
    app.include_router(kudos.router, prefix="/activities", tags=["Kudos"])

    return app


# Module-level ASGI app for `uvicorn strava.main:app` (no --factory needed).
# Safe at import: create_app() only builds the app + routers; Settings()/DB
# initialisation happen in the lifespan handler at startup, not here.
app = create_app()
