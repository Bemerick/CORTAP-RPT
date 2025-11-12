# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml ./
# COPY uv.lock ./  # optional if available

ARG INSTALL_EXTRAS=prod
RUN uv pip install --system --no-cache ".[${INSTALL_EXTRAS}]"

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /usr/local /usr/local

COPY ./app ./app
COPY ./alembic.ini ./
COPY ./alembic ./alembic

# Run Alembic migrations on startup
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Non-root user
RUN useradd -m appuser
USER appuser

# Make sure the app, alembic, and writable dirs are owned by appuser
RUN mkdir -p /app/data /app/logs \
    && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

ENTRYPOINT ["docker-entrypoint.sh"]

HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
