#!/bin/bash
# Startup script for Railway deployment
# Runs database migrations before starting the app

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}