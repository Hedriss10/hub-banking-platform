"""Integração real com PostgreSQL (Testcontainers)."""

import pytest
from sqlalchemy import text
from starlette import status

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope='session')
async def test_async_session_connects_to_postgres(integration_database_ready: None):
    from src.infrastructure.database.session import get_session

    async for session in get_session(verify_connection=True):
        result = await session.execute(text('SELECT 1'))
        assert result.scalar_one() == 1


def test_openapi_available(integration_client):
    response = integration_client.get('/openapi.json')
    assert response.status_code == status.HTTP_200_OK
    assert 'openapi' in response.json()
