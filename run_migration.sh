#!/bin/bash

# Replace this with YOUR Railway database URL from the Connect tab
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@YOUR_HOST.railway.app:PORT/railway"

# Run the migration
psql "$DATABASE_URL" < RUN_THIS_SQL_NOW.sql

echo "Migration complete!"