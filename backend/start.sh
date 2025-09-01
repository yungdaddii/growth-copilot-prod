#!/bin/sh
echo "=========================================="
echo "=== Starting Growth Copilot Backend ==="
echo "=== DEPLOYMENT: v2.1-POST-FIX ==="
echo "=== Google Ads Fix: POST for listAccessibleCustomers ==="
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
alembic upgrade head || echo "Alembic migrations failed or no migrations to run"

# Create user_contexts table directly if needed
echo "Ensuring user_contexts table exists..."
python -c "
import asyncio
from sqlalchemy import text
from app.database import engine

async def ensure_table():
    sql = '''
    CREATE TABLE IF NOT EXISTS user_contexts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id VARCHAR(255) NOT NULL UNIQUE,
        primary_domain VARCHAR(255),
        competitors TEXT[],
        industry VARCHAR(255),
        company_size VARCHAR(50),
        monitoring_sites JSONB,
        preferences JSONB,
        last_analysis TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT now(),
        updated_at TIMESTAMP NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_user_contexts_session_id ON user_contexts(session_id);
    '''
    try:
        async with engine.begin() as conn:
            await conn.execute(text(sql))
        print('✅ user_contexts table ready')
    except Exception as e:
        print(f'Table creation failed: {e}')

asyncio.run(ensure_table())
" || echo "Table creation skipped"
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