from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import settings

# Create async engine
# For Supabase transaction pooler, we need special settings
if "pooler.supabase.com:6543" in settings.DATABASE_URL:
    # Transaction pooler mode - disable prepared statements completely
    # Add prepared_statement_cache_size=0 to the URL
    db_url = settings.DATABASE_URL
    if "?" in db_url:
        db_url += "&prepared_statement_cache_size=0"
    else:
        db_url += "?prepared_statement_cache_size=0"
    
    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        poolclass=NullPool,  # Use NullPool for transaction pooler
        connect_args={
            "server_settings": {
                "jit": "off",
                "application_name": "growthcopilot"
            },
            "command_timeout": 60,
            "prepared_statement_cache_size": 0,
        }
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

# Base class for models
Base = declarative_base()


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