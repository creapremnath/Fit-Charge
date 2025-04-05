#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head  # Ensure alembic is properly set up

echo "Starting FastAPI app with Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
