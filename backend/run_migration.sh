#!/bin/bash

# Get the DATABASE_URL from Railway and convert asyncpg to postgresql for Alembic
echo "Getting DATABASE_URL from Railway..."
DB_URL=$(railway variables -k | grep "DATABASE_URL=" | cut -d'=' -f2-)

# Check if we got the URL
if [ -z "$DB_URL" ]; then
    echo "Error: Could not get DATABASE_URL from Railway"
    echo "Please run: railway variables -k"
    exit 1
fi

# Replace postgresql+asyncpg with postgresql for synchronous connection
# Handle both formats: postgresql+asyncpg:// and asyncpg://
if [[ $DB_URL == *"postgresql+asyncpg"* ]]; then
    DB_URL_SYNC=${DB_URL//postgresql+asyncpg/postgresql}
elif [[ $DB_URL == *"asyncpg://"* ]]; then
    DB_URL_SYNC=${DB_URL//asyncpg:\/\//postgresql:\/\/}
else
    # Already in sync format
    DB_URL_SYNC=$DB_URL
fi

echo "Running migration with synchronized database URL..."
DATABASE_URL="$DB_URL_SYNC" railway run alembic upgrade head

echo "Migration complete!"