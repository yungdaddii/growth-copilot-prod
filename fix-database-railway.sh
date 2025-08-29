#!/bin/bash

echo "Updating Railway DATABASE_URL to use Supabase direct connection..."
echo ""
echo "This switches from transaction pooler (port 6543) to direct connection (port 5432)"
echo "Direct connection is more compatible with SQLAlchemy/asyncpg"

# Use direct connection instead of pooler
railway variables --set DATABASE_URL="postgresql+asyncpg://postgres:GyND6conm8NqiFTv@db.evfltcejtkodoqrshizs.supabase.co:5432/postgres"

echo ""
echo "✅ DATABASE_URL updated to use direct connection!"
echo "Railway will automatically redeploy."
echo ""
echo "Note: Direct connection is better for persistent connections like Railway."