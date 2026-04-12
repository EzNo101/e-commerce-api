import json
from typing import Any
from redis.asyncio import Redis
from app.core.config import settings


class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Any | None:
        raw = await self.redis.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            await self.redis.delete(key)
            return None

    async def set(self, key: str, value: Any) -> None:
        await self.redis.setex(key, settings.CACHE_TTL, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        async for key in self.redis.scan_iter(match=pattern):  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            await self.redis.delete(key)  # pyright: ignore[reportUnknownArgumentType]
