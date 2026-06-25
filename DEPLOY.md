# Strava MVP — Deploy Guide

Production-focused walkthrough for standing up the Strava MVP stack.

## Prerequisites

- **Docker** 24+ and **Docker Compose** v2+
- Port `8010` available on the host (configurable via `APP_PORT`)

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url> strava && cd strava

# 2. (Optional) Create .env to customise settings
cp .env.example .env

# 3. Bring the stack up
docker compose up -d

# 4. Verify it's alive
curl http://localhost:8010/healthz
# → {"status":"ok"}
```

## Environment Variables

All variables have safe defaults. Override them in a `.env` file or directly in the shell.

| Variable | Default | Description |
|---|---|---|
| `APP_PORT` | `8010` | Host port the app is published on |
| `HOST` | `0.0.0.0` | Bind address inside the container |
| `LOG_LEVEL` | `info` | Uvicorn log level |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/strava` | Async database connection string |

## Database

- **PostgreSQL 16** runs in the `db` service (Alpine-based, not exposed to the host).
- **Schema migrations** run automatically on every app container startup (`alembic upgrade head`).
- Data persists in the `pgdata` named volume — survives `docker compose down`.

## Service Layout

| Service | Image / Build | Internal Port | Host Port | Healthcheck |
|---|---|---|---|---|
| `db` | `postgres:16-alpine` | 5432 (compose network only) | — | `pg_isready` |
| `app` | Built from `Dockerfile` | 8000 | `${APP_PORT:-8010}` | `curl /healthz` |

Only the `app` service publishes a host port. The database is reachable only over the compose network.

## Stop / Restart

```bash
# Stop (preserves volume data)
docker compose down

# Stop and wipe the database
docker compose down -v

# Restart
docker compose up -d

# View logs
docker compose logs -f app

# Check service health
docker compose ps
```

## Health Endpoint

```bash
curl -s http://localhost:8010/healthz | python -m json.tool
```

Returns `{"status": "ok"}` (200) when the app and database are healthy. Returns `{"status": "degraded", "detail": "database unreachable"}` (503) when the database is down.
