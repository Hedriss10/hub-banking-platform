from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import src.interface.api.v2.routes.health_check as health_check_module
from httpx import AsyncClient
from src.interface.api.v2.routes.health_check import (
    _check_application,
    _check_database,
    _check_redis,
    _overall_status,
)
from src.interface.api.v2.schemas.health_check import ComponentHealthSchema
from starlette import status

pytestmark = pytest.mark.unit

_HEALTH = '/api/v2/health'


def _settings(*, redis_url: str | None = 'redis://localhost:6379/0') -> SimpleNamespace:
    return SimpleNamespace(
        APP_NAME='hub-banking-platform',
        API_VERSION='2.0.0',
        REDIS_URL=redis_url,
    )


class _ConnectCM:
    def __init__(self, connection: AsyncMock) -> None:
        self._connection = connection

    async def __aenter__(self) -> AsyncMock:
        return self._connection

    async def __aexit__(self, *_args: object) -> None:
        return None


def _mock_db_engine(*, execute_error: Exception | None = None) -> MagicMock:
    connection = AsyncMock()
    if execute_error is not None:
        connection.execute = AsyncMock(side_effect=execute_error)
    else:
        connection.execute = AsyncMock(return_value=None)

    engine = MagicMock()
    engine.connect = MagicMock(return_value=_ConnectCM(connection))
    return engine


@pytest.mark.asyncio
async def test_check_application_returns_healthy() -> None:
    result = await _check_application()

    assert result.status == 'healthy'
    assert result.detail is None


@pytest.mark.asyncio
async def test_check_database_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health_check_module, 'get_engine', _mock_db_engine)

    result = await _check_database()

    assert result.status == 'healthy'
    assert result.detail is None


@pytest.mark.asyncio
async def test_check_database_unhealthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        health_check_module,
        'get_engine',
        partial(_mock_db_engine, execute_error=OSError('connection refused')),
    )

    result = await _check_database()

    assert result.status == 'unhealthy'
    assert result.detail == 'connection refused'


@pytest.mark.asyncio
async def test_check_redis_without_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        health_check_module,
        'get_settings',
        partial(_settings, redis_url=None),
    )

    result = await _check_redis()

    assert result.status == 'unhealthy'
    assert result.detail == 'REDIS_URL não configurado'


@pytest.mark.asyncio
async def test_check_redis_ping_false(monkeypatch: pytest.MonkeyPatch) -> None:
    redis_client = AsyncMock()
    redis_client.ping = AsyncMock(return_value=False)
    monkeypatch.setattr(health_check_module, 'get_settings', _settings)
    monkeypatch.setattr(
        health_check_module,
        'get_redis_client',
        AsyncMock(return_value=redis_client),
    )

    result = await _check_redis()

    assert result.status == 'unhealthy'
    assert result.detail == 'Redis não respondeu ao PING'


@pytest.mark.asyncio
async def test_check_redis_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health_check_module, 'get_settings', _settings)
    monkeypatch.setattr(
        health_check_module,
        'get_redis_client',
        AsyncMock(side_effect=ConnectionError('redis down')),
    )

    result = await _check_redis()

    assert result.status == 'unhealthy'
    assert result.detail == 'redis down'


@pytest.mark.asyncio
async def test_check_redis_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    redis_client = AsyncMock()
    redis_client.ping = AsyncMock(return_value=True)
    monkeypatch.setattr(health_check_module, 'get_settings', _settings)
    monkeypatch.setattr(
        health_check_module,
        'get_redis_client',
        AsyncMock(return_value=redis_client),
    )

    result = await _check_redis()

    assert result.status == 'healthy'
    assert result.detail is None


def test_overall_status_healthy() -> None:
    checks = (
        ComponentHealthSchema(status='healthy'),
        ComponentHealthSchema(status='healthy'),
    )

    assert _overall_status(*checks) == 'healthy'


def test_overall_status_unhealthy() -> None:
    checks = (
        ComponentHealthSchema(status='healthy'),
        ComponentHealthSchema(status='unhealthy', detail='fail'),
    )

    assert _overall_status(*checks) == 'unhealthy'


@pytest.mark.asyncio
async def test_health_check_all_healthy(
    async_v2_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(health_check_module, 'get_settings', _settings)
    monkeypatch.setattr(health_check_module, 'get_engine', _mock_db_engine)
    redis_client = AsyncMock()
    redis_client.ping = AsyncMock(return_value=True)
    monkeypatch.setattr(
        health_check_module,
        'get_redis_client',
        AsyncMock(return_value=redis_client),
    )

    response = await async_v2_client.get(_HEALTH)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body['status'] == 'healthy'
    assert body['app_name'] == 'hub-banking-platform'
    assert body['version'] == '2.0.0'
    assert body['checks']['application']['status'] == 'healthy'
    assert body['checks']['database']['status'] == 'healthy'
    assert body['checks']['redis']['status'] == 'healthy'


@pytest.mark.asyncio
async def test_health_check_unhealthy(
    async_v2_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        health_check_module,
        'get_settings',
        partial(_settings, redis_url=None),
    )
    monkeypatch.setattr(
        health_check_module,
        'get_engine',
        partial(_mock_db_engine, execute_error=OSError('db down')),
    )

    response = await async_v2_client.get(_HEALTH)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    body = response.json()
    assert body['status'] == 'unhealthy'
    assert body['checks']['database']['status'] == 'unhealthy'
    assert body['checks']['redis']['status'] == 'unhealthy'
