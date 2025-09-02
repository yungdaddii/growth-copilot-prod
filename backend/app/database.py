from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.config import settings
from app.database_base import Base  # Import shared Base

logger = logging.getLogger(__name__)

# Create async engine
# Check if we're using Supabase pooler
if "pooler.supabase.com" in settings.DATABASE_URL:
    # Use session pooler on port 5432 instead of transaction pooler
    # Session pooler handles prepared statements better
    db_url = settings.DATABASE_URL.replace(":6543", ":5432")
    logger.info("Switched from Supabase transaction pooler to session pooler")
    
    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections every 5 minutes
    )
else:
    # Direct connection or other database
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()