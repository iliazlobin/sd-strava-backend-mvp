# Strava MVP

Backend service for a fitness social network — record GPS-tracked activities, define segments,
rank efforts on leaderboards, and give kudos.

## Quickstart

```bash
# Clone and enter the project
git clone <repo-url> strava && cd strava

# (Optional) Customize environment
cp .env.example .env

# Start the stack (requires Docker)
docker compose up -d

# Verify it's alive
curl http://localhost:8010/healthz
# → {"status":"ok"}
```

## Architecture

Monolithic REST API built on **FastAPI** with **PostgreSQL 16** for persistence. The app
talks to the database over async SQLAlchemy 2.0 and auto-runs Alembic migrations on startup.

```
Client (REST)  →  FastAPI  →  SQLAlchemy (asyncpg)  →  PostgreSQL
```

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · asyncpg · Alembic · Pydantic v2

No message queues, caches, or external streaming infrastructure in this MVP. GPS polylines
are stored as JSONB columns. Segment matching is client-submitted; the leaderboard is a
plain indexed SQL query.

## API Reference

All IDs are UUIDv4 strings. All timestamps are ISO 8601. Error shapes are documented in
`DESIGN.md`.

### Users

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `POST` | `/users` | Create a user | `curl -X POST localhost:8010/users -H 'Content-Type: application/json' -d '{"display_name":"Alice"}'` |

### Activities

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `POST` | `/activities` | Record an activity | `curl -X POST localhost:8010/activities -H 'Content-Type: application/json' -d '{"user_id":"<uuid>","sport_type":"run","start_time":"2025-06-25T08:00:00Z","elapsed_time":1800,"distance_m":5000.0,"polyline":[[40.71,-74.0,10.0,1719907200]]}'` |
| `GET` | `/activities/{id}` | Get activity detail | `curl localhost:8010/activities/<uuid>` |
| `GET` | `/users/{user_id}/activities` | List user activities (paginated) | `curl 'localhost:8010/users/<uuid>/activities?limit=10&offset=0'` |

### Segments

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `POST` | `/segments` | Define a segment | `curl -X POST localhost:8010/segments -H 'Content-Type: application/json' -d '{"name":"Hill Climb","polyline":[[40.71,-74.0,5.0,1719907200]],"distance_m":1200.0}'` |
| `GET` | `/segments/{id}` | Get segment detail | `curl localhost:8010/segments/<uuid>` |

### Efforts & Leaderboard

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `POST` | `/segment-efforts` | Record a segment effort | `curl -X POST localhost:8010/segment-efforts -H 'Content-Type: application/json' -d '{"activity_id":"<uuid>","segment_id":"<uuid>","user_id":"<uuid>","elapsed_time":305}'` |
| `GET` | `/segments/{id}/leaderboard` | Top-N leaderboard | `curl 'localhost:8010/segments/<uuid>/leaderboard?limit=10'` |

### Kudos

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `POST` | `/activities/{id}/kudos` | Give kudos (idempotent) | `curl -X POST localhost:8010/activities/<uuid>/kudos -H 'Content-Type: application/json' -d '{"user_id":"<uuid>"}'` |
| `GET` | `/activities/{id}/kudos` | List kudos | `curl localhost:8010/activities/<uuid>/kudos` |

### Health

| Method | Path | Purpose | Example |
|--------|------|---------|---------|
| `GET` | `/healthz` | Health check (DB ping included) | `curl localhost:8010/healthz` |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `APP_PORT` | `8010` | Host port the app publishes on |
| `HOST` | `0.0.0.0` | Bind address inside the container |
| `LOG_LEVEL` | `info` | Uvicorn log level |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/strava` | Database connection string |

All variables are set in `docker-compose.yml` with safe defaults. Override them in a `.env`
file or directly in the shell.

## Testing

### Unit tests (white-box)

```bash
pip install -e '.[dev]'
pytest tests/ -v
```

Unit tests exercise application internals (models, services) with an in-memory SQLite backend
and mocked dependencies.

### Acceptance tests (black-box)

```bash
# Requires a running app at API_BASE_URL (default http://localhost:8000)
pytest verify/acceptance/ -v

# Against Docker Compose (host-only)
API_BASE_URL=http://localhost:8010 pytest verify/acceptance/ -v
```

Acceptance tests talk to the running system over HTTP and assert real input → output
(status codes, bodies, error cases, idempotency). One test file per functional requirement.

## Deploy

See `DEPLOY.md` for a full production guide, service layout, and database management.

### CI/CD

`.github/workflows/` contains lint and test pipelines. Unit tests run on every push;
a combined unit + acceptance job validates the full stack.

## Limitations

This is an MVP. The following are out of scope:

- **No real GPS streaming pipeline** — polylines are stored as JSONB arrays, not streamed
  through Kafka to S3/Parquet
- **No automatic segment matching** — efforts are explicitly submitted by the client;
  H3 hex pre-filter + DTW matching is deferred
- **No social feed** — user follows, follower timelines, and Redis feed caching are not
  implemented
- **No Redis / ScyllaDB** — leaderboards use a PostgreSQL indexed query
- **No offline recording or sync**
- **No comments, anti-cheat, or moderation**
