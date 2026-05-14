from typing import Optional

import redis.asyncio as redis

from src.core.config.settings import get_settings

_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Cliente singleton Redis (async)."""
    global _redis_client

    settings = get_settings()
    if not settings.REDIS_URL:
        raise RuntimeError(
            'REDIS_URL não configurado — necessário para jobs '
            'em segundo plano (batch Safra).'
        )

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

    return _redis_client
