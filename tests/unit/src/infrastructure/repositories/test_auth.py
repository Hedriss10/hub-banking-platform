"""Testes do repositório de autenticação (Postgres)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from src.core.exceptions.custom import DatabaseException
from src.infrastructure.repositories import auth_postgres as auth_postgres_module
from src.infrastructure.repositories.auth_postgres import AuthPostgresRepository
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def auth_repository(mock_session: AsyncMock) -> AuthPostgresRepository:
    return AuthPostgresRepository(mock_session)


@pytest.mark.asyncio
async def test_find_employee_by_email_success(
    auth_repository: AuthPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)

    expected = build_employee_dto()
    monkeypatch.setattr(
        auth_postgres_module.EmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _obj: expected),
    )

    out = await auth_repository.find_employee_by_email('a@example.com')

    assert out is expected
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_employee_by_email_not_found(
    auth_repository: AuthPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=result_mock)

    out = await auth_repository.find_employee_by_email('missing@example.com')

    assert out is None


@pytest.mark.asyncio
async def test_find_employee_by_email_sqlalchemy_error(
    auth_repository: AuthPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await auth_repository.find_employee_by_email('x@y.z')

    mock_session.rollback.assert_awaited_once()
