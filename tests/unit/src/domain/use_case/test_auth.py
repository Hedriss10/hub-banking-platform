"""Testes do caso de uso Auth — delegação ao serviço."""

from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.auth import AccessTokenDTO, LoginDTO
from src.domain.use_case.auth import AuthUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_delegates_to_service() -> None:
    login = LoginDTO(email='u@example.com', password='secret')
    expected = AccessTokenDTO(access_token='tok')

    service = AsyncMock()
    service.login = AsyncMock(return_value=expected)
    use_case = AuthUseCase(service)

    result = await use_case.login(login)

    assert result == expected
    service.login.assert_awaited_once_with(login)
