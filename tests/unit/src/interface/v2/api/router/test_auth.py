from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from src.domain.dtos.auth import AccessTokenDTO
from starlette import status

pytestmark = pytest.mark.unit

_LOGIN = '/api/v2/login'


@pytest.mark.asyncio
async def test_post_login(
    async_auth_client: AsyncClient,
    mock_auth_use_case: AsyncMock,
) -> None:
    mock_auth_use_case.login = AsyncMock(
        return_value=AccessTokenDTO(access_token='token', token_type='bearer'),
    )

    response = await async_auth_client.post(
        _LOGIN,
        json={'email': 'u@example.com', 'password': 'secret'},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body['access_token'] == 'token'
    assert body['token_type'] == 'bearer'
    mock_auth_use_case.login.assert_awaited_once()
