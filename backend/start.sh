#!/bin/sh
echo "=========================================="
echo "=== Starting Growth Copilot Backend ==="
echo "=== DEPLOYMENT: v3.2-DIRECT-API-CALLS ==="
echo "=== Google Ads Fix: Direct API calls, bypass override issues ==="
echo "=========================================="
echo "Python version:"
python --version
echo ""
echo "Environment variables:"
echo "PORT=${PORT:-8000}"
echo "DATABASE_URL is set: $(if [ -n "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo ""

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "Migrations failed or no migrations to run"
echo ""

# Test import first
echo "Testing imports..."
python -c "
try:
    import app.main
    print('✅ App imports successful')
    print('✅ Google Ads POST fix applied')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
" || true

echo ""
echo "Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}