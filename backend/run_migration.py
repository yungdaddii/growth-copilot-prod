#!/usr/bin/env python3
"""
Run database migration to create user_contexts table.
Execute this directly on Railway if migrations aren't running automatically.
"""

import asyncio
import os
from sqlalchemy import text
from app.database import engine

async def create_user_contexts_table():
    """Create the user_contexts table directly."""
    
    create_table_sql = """
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
    """
    
    async with engine.begin() as conn:
        await conn.execute(text(create_table_sql))
        print("✅ user_contexts table created successfully")

if __name__ == "__main__":
    asyncio.run(create_user_contexts_table())