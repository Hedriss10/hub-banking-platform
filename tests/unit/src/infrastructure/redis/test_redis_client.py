from types import SimpleNamespace
from unittest.mock import MagicMock

import fakeredis.aioredis
import pytest
import src.infrastructure.redis.client as redis_client_module
from src.infrastructure.redis.client import get_redis_client

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_redis_singleton() -> None:
    redis_client_module._redis_client = None
    yield
    redis_client_module._redis_client = None


@pytest.mark.asyncio
async def test_get_redis_client_exige_redis_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        redis_client_module,
        'get_settings',
        lambda: SimpleNamespace(REDIS_URL=None),
    )
    with pytest.raises(RuntimeError, match='REDIS_URL'):
        await get_redis_client()


@pytest.mark.asyncio
async def test_get_redis_client_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    spy = MagicMock(return_value=fake)
    monkeypatch.setattr(redis_client_module.redis, 'from_url', spy)
    monkeypatch.setattr(
        redis_client_module,
        'get_settings',
        lambda: SimpleNamespace(REDIS_URL='redis://localhost'),
    )

    first = await get_redis_client()
    second = await get_redis_client()

    assert first is second
    spy.assert_called_once()
