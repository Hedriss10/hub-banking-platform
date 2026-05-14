from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import fakeredis.aioredis
import pytest
import src.infrastructure.redis.client as redis_client_module
from src.infrastructure.redis.safra_batch_job_store import job_get, job_save

pytestmark = pytest.mark.unit

_TOTAL_ROWS_FIXTURE = 3


@pytest.fixture(autouse=True)
def reset_redis_singleton() -> None:
    redis_client_module._redis_client = None
    yield
    redis_client_module._redis_client = None


@pytest.mark.asyncio
async def test_job_save_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(
        redis_client_module.redis, 'from_url', MagicMock(return_value=fake)
    )
    monkeypatch.setattr(
        redis_client_module,
        'get_settings',
        lambda: SimpleNamespace(
            REDIS_URL='redis://localhost',
            SAFRA_BATCH_JOB_TTL_SECONDS=3600,
        ),
    )

    jid = uuid4()
    payload = {
        'status': 'queued',
        'total_rows': _TOTAL_ROWS_FIXTURE,
        'processed_rows': 0,
        'failed_rows': 0,
        'detail': None,
    }
    await job_save(jid, payload)
    loaded = await job_get(jid)

    assert loaded is not None
    assert loaded['status'] == 'queued'
    assert loaded['total_rows'] == _TOTAL_ROWS_FIXTURE


@pytest.mark.asyncio
async def test_job_get_ausente(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(
        redis_client_module.redis, 'from_url', MagicMock(return_value=fake)
    )
    monkeypatch.setattr(
        redis_client_module,
        'get_settings',
        lambda: SimpleNamespace(
            REDIS_URL='redis://localhost',
            SAFRA_BATCH_JOB_TTL_SECONDS=3600,
        ),
    )

    assert await job_get(uuid4()) is None
