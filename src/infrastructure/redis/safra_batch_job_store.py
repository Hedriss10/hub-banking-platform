import json
from typing import Any, Optional
from uuid import UUID

from src.core.config.settings import get_settings
from src.infrastructure.redis.client import get_redis_client

_JOB_KEY = 'safra:batch:job:{job_id}'


def _key(job_id: UUID) -> str:
    return _JOB_KEY.format(job_id=job_id)


async def job_save(job_id: UUID, payload: dict[str, Any]) -> None:
    result = await get_redis_client()
    settings = get_settings()
    await result.set(
        _key(job_id), json.dumps(payload), ex=settings.SAFRA_BATCH_JOB_TTL_SECONDS
    )


async def job_get(job_id: UUID) -> Optional[dict[str, Any]]:
    result = await get_redis_client()
    raw = await result.get(_key(job_id))
    if raw is None:
        return None
    return json.loads(raw)
