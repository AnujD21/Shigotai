#!/bin/sh
set -e

echo "Running database migrations..."
python -m alembic upgrade head

if [ "$DEMO_MODE" = "true" ]; then
  echo "DEMO_MODE=true -- seeding demo data if the database is empty..."
  python -m app.seed || true
fi

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
