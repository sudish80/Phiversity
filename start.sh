#!/bin/sh

set -eu

echo "Starting Phiversity service..."

mkdir -p media/videos media/images media/texts voice_cache web_jobs

export MANIM_QUALITY="${MANIM_QUALITY:-low}"
export JOB_TIMEOUT="${JOB_TIMEOUT:-600}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export SERVICE_MODE="${SERVICE_MODE:-api}"
export RUN_DB_MIGRATIONS_ON_STARTUP="${RUN_DB_MIGRATIONS_ON_STARTUP:-false}"

echo "Configuration:"
echo "  mode: ${SERVICE_MODE}"
echo "  quality: ${MANIM_QUALITY}"
echo "  timeout: ${JOB_TIMEOUT}s"
echo "  storage: ${STORAGE_BACKEND:-local}"
echo "  migrations-on-startup: ${RUN_DB_MIGRATIONS_ON_STARTUP}"

if [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "WARNING: No LLM API keys configured."
fi

if [ "${SERVICE_MODE}" = "worker" ]; then
  echo "Starting background worker..."
  exec python -m scripts.server.run_worker
fi

if [ "${RUN_DB_MIGRATIONS_ON_STARTUP}" = "true" ]; then
  if ! command -v alembic >/dev/null 2>&1; then
    echo "ERROR: alembic CLI is not installed but RUN_DB_MIGRATIONS_ON_STARTUP=true"
    exit 1
  fi
  echo "Running database migrations..."
  alembic upgrade head
fi

echo "Starting API server on ${HOST}:${PORT}..."
exec python -m uvicorn scripts.server.app:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --workers 1
