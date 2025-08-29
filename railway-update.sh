#!/bin/bash

# Railway environment variable update script
# Run this script to update your Railway deployment with the new Supabase database URL

echo "Updating Railway environment variables..."

# First, ensure you're logged in to Railway
railway login

# Link to your project (if not already linked)
railway link

# Set the new DATABASE_URL
railway variables --set DATABASE_URL="postgresql+asyncpg://postgres.evfltcejtkodoqrshizs:GyND6conm8NqiFTv@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

echo "Environment variables updated!"
echo "Your Railway app will automatically redeploy with the new database connection."
echo ""
echo "Monitor the deployment at: https://railway.app/project/growth-copilot-prod"