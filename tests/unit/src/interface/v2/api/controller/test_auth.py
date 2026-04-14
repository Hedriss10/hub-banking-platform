"""Testes do controller de autenticação."""

from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.auth import AccessTokenDTO
from src.interface.api.v2.controller.auth import AuthController
from src.interface.api.v2.schemas.auth import LoginRequestSchema

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_maps_schema_to_dto_and_response() -> None:
    use_case = AsyncMock()
    use_case.login = AsyncMock(
        return_value=AccessTokenDTO(access_token='jwt-here', token_type='bearer'),
    )
    controller = AuthController(use_case)

    body = LoginRequestSchema(email='a@b.co', password='pwd')
    result = await controller.login(body)

    assert result.access_token == 'jwt-here'
    assert result.token_type == 'bearer'
    use_case.login.assert_awaited_once()
