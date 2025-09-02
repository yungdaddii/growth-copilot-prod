#!/bin/bash

# Get the DATABASE_URL from Railway and convert asyncpg to postgresql for Alembic
echo "Getting DATABASE_URL from Railway..."
DB_URL=$(railway variables | grep "DATABASE_URL" | head -1 | awk -F'│' '{print $2}' | xargs)

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

echo "Original URL: $DB_URL"
echo "Sync URL: $DB_URL_SYNC"
echo "Running migration..."
DATABASE_URL="$DB_URL_SYNC" alembic upgrade head

echo "Migration complete!"