#!/bin/bash
# Startup script for Railway deployment
# Runs database migrations before starting the app

echo "==================================="
echo "DEPLOYMENT VERSION: v2.1-POST-FIX"
echo "Google Ads Fix: POST for listAccessibleCustomers"
echo "==================================="

echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to run"

echo "Starting application on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}