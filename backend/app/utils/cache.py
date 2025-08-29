import redis.asyncio as redis
import json
from typing import Any, Optional
import structlog

from app.config import settings

logger = structlog.get_logger()

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        redis_client = None


async def get_redis() -> Optional[redis.Redis]:
    return redis_client


async def cache_result(key: str, value: Any, ttl: int = None) -> bool:
    if not redis_client:
        return False
    
    try:
        ttl = ttl or settings.CACHE_TTL
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await redis_client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        logger.error("Cache set failed", key=key, error=str(e))
        return False


async def get_cached_result(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    
    try:
        value = await redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
    except Exception as e:
        logger.error("Cache get failed", key=key, error=str(e))
    
    return None


async def delete_cache(key: str) -> bool:
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error("Cache delete failed", key=key, error=str(e))
        return False


async def clear_pattern(pattern: str) -> int:
    if not redis_client:
        return 0
    
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error("Cache clear pattern failed", pattern=pattern, error=str(e))
        return 0