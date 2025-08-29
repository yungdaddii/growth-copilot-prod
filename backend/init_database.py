#!/usr/bin/env python3
"""Initialize database schema for Supabase deployment"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from app.models.base import Base
from app.models.conversation import Conversation, Message
from app.models.analysis import Analysis, CompetitorCache
from app.models.benchmarks import IndustryBenchmark
from app.models.context import UserContext, SiteSnapshot, CompetitorIntelligence, GrowthBenchmark, GrowthExperiment
from app.models.integration import Integration

# Load environment variables
load_dotenv('../.env')

async def init_database():
    """Create all tables in the database"""
    try:
        print("🔧 Initializing database schema...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database schema created successfully!")
        
        # List created tables
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = result.fetchall()
            
            print("\n📋 Created tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())