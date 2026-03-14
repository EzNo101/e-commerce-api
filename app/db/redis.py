import logging
import redis.asyncio as redis
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisState:
    client: Optional[redis.Redis] = None

state = RedisState()

async def init_redis() -> None:
    if not settings.REDIS_URL:
        logger.info("Redis URL is not set. Skipping redis init.")
        return

    try:
        state.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
        await state.client.ping()
        logger.info("Redis connected.")
    except Exception as exc:
        logger.error(f"Redis connection failed: {exc}")
        state.client = None

async def close_redis() -> None:
    if state.client is not None:
        await state.client.aclose()
        state.client = None
        logger.info("Redis connection closed.")

async def get_redis() -> Optional[redis.Redis]:
    return state.client