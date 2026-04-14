"""Testes do serviço de autenticação."""

from unittest.mock import AsyncMock, patch

import pytest
from src.domain.dtos.auth import LoginDTO
from src.domain.exceptions.auth import InvalidCredentialsException
from src.domain.service.auth import AuthService
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_success_returns_access_token() -> None:
    employee = build_employee_dto(email='ok@example.com', password='stored-hash')
    repo = AsyncMock()
    repo.find_employee_by_email = AsyncMock(return_value=employee)

    with (
        patch('src.domain.service.auth.verify_password', return_value=True),
        patch(
            'src.domain.service.auth.create_access_token',
            return_value='signed.jwt.token',
        ),
    ):
        service = AuthService(repo)
        result = await service.login(
            LoginDTO(email='ok@example.com', password='plain'),
        )

    assert result.access_token == 'signed.jwt.token'
    assert result.token_type == 'bearer'
    repo.find_employee_by_email.assert_awaited_once_with('ok@example.com')


@pytest.mark.asyncio
async def test_login_raises_when_employee_not_found() -> None:
    repo = AsyncMock()
    repo.find_employee_by_email = AsyncMock(return_value=None)
    service = AuthService(repo)

    with pytest.raises(InvalidCredentialsException, match='inválidos'):
        await service.login(LoginDTO(email='nope@example.com', password='x'))


@pytest.mark.asyncio
async def test_login_raises_when_password_invalid() -> None:
    employee = build_employee_dto()
    repo = AsyncMock()
    repo.find_employee_by_email = AsyncMock(return_value=employee)
    service = AuthService(repo)

    with patch('src.domain.service.auth.verify_password', return_value=False):
        with pytest.raises(InvalidCredentialsException, match='inválidos'):
            await service.login(LoginDTO(email=employee.email, password='wrong'))
