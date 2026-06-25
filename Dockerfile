# Multi-stage build for Strava MVP
# Stage 1: Builder — install dependencies
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir --prefix=/install \
    fastapi>=0.115,<1.0 \
    uvicorn[standard]>=0.30,<1.0 \
    sqlalchemy[asyncio]>=2.0,<3.0 \
    asyncpg>=0.29,<1.0 \
    alembic>=1.13,<2.0 \
    pydantic>=2.0,<3.0 \
    pydantic-settings>=2.0,<3.0

# Stage 2: Runtime — slim production image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ src/
COPY alembic.ini .
COPY alembic/ alembic/

EXPOSE 8000

CMD alembic upgrade head && uvicorn strava.main:create_app --factory --host 0.0.0.0 --port 8000
