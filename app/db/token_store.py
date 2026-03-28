from redis.asyncio import Redis

REFRESH_TOKEN_PREFIX = "refresh_token"


def _build_refresh_token_key(jti: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}:{jti}"


async def store_refresh_token(
    client: Redis, jti: str, user_id: int, expires_in: int
) -> None:
    await client.set(_build_refresh_token_key(jti), str(user_id), ex=expires_in)


async def get_refresh_token_owner(client: Redis, jti: str) -> str | None:
    return await client.get(_build_refresh_token_key(jti))


async def delete_refresh_token(client: Redis, jti: str) -> None:
    await client.delete(_build_refresh_token_key(jti))
