from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.employee import EmployeeDTO, EmployeeUpdateDTO
from src.domain.enum.employee_role import EmployeeRole
from src.infrastructure.repositories import (
    employee_postgres as employee_postgres_module,
)
from src.infrastructure.repositories.employee_postgres import EmployeeRepositoryPostgres
from tests.fixtures.employee_factories import (
    build_employee_dto,
    build_employee_update_dto,
)

pytestmark = pytest.mark.unit


def _integrity_unique() -> IntegrityError:
    orig = MagicMock()
    orig.pgcode = '23505'
    orig.sqlstate = None
    return IntegrityError('stmt', None, orig)


def _integrity_fk() -> IntegrityError:
    orig = MagicMock()
    orig.pgcode = '23503'
    orig.sqlstate = None
    return IntegrityError('stmt', None, orig)


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def repository(mock_session: AsyncMock) -> EmployeeRepositoryPostgres:
    return EmployeeRepositoryPostgres(mock_session)


@pytest.mark.asyncio
async def test_create_employee_success(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_create_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(employee_postgres_module, 'hash_password', lambda _p: 'hashed')

    async def _refresh(obj: object) -> None:
        setattr(obj, 'id', uuid4())
        now = datetime.now(timezone.utc)
        setattr(obj, 'created_at', now)
        setattr(obj, 'updated_at', now)

    mock_session.refresh = AsyncMock(side_effect=_refresh)

    result = await repository.create_employee(employee_create_dto)

    assert isinstance(result, EmployeeDTO)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_employee_duplicate_raises_duplicated(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_create_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(employee_postgres_module, 'hash_password', lambda _p: 'hashed')
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())

    with pytest.raises(DuplicatedException):
        await repository.create_employee(employee_create_dto)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_employee_integrity_other_raises_database(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_create_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(employee_postgres_module, 'hash_password', lambda _p: 'hashed')
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())

    with pytest.raises(DatabaseException):
        await repository.create_employee(employee_create_dto)


@pytest.mark.asyncio
async def test_create_employee_sqlalchemy_error(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_create_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(employee_postgres_module, 'hash_password', lambda _p: 'hashed')
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.create_employee(employee_create_dto)


@pytest.mark.asyncio
async def test_get_employee_by_id_success(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)

    monkeypatch.setattr(
        employee_postgres_module.EmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _obj: build_employee_dto()),
    )

    out = await repository.get_employee_by_id(uuid4())

    assert isinstance(out, EmployeeDTO)


@pytest.mark.asyncio
async def test_get_employee_by_id_none(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
) -> None:
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=result_mock)

    out = await repository.get_employee_by_id(uuid4())

    assert out is None


@pytest.mark.asyncio
async def test_get_employee_by_id_sqlalchemy_error(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.get_employee_by_id(uuid4())


@pytest.mark.asyncio
async def test_update_employee_empty_payload_returns_current(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = build_employee_dto()
    monkeypatch.setattr(
        repository,
        'get_employee_by_id',
        AsyncMock(return_value=dto),
    )

    result = await repository.update_employee(dto.id, EmployeeUpdateDTO())

    assert result == dto
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_update_employee_empty_payload_not_found_raises(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        'get_employee_by_id',
        AsyncMock(return_value=None),
    )

    with pytest.raises(DatabaseException, match='Employee not found'):
        await repository.update_employee(uuid4(), EmployeeUpdateDTO())


@pytest.mark.asyncio
async def test_update_employee_converts_role_in_payload(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = EmployeeUpdateDTO(role=EmployeeRole.ADMIN)
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)

    monkeypatch.setattr(
        employee_postgres_module.EmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _obj: build_employee_dto()),
    )

    await repository.update_employee(employee_dto.id, payload)

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_employee_success_returns_dto(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = build_employee_update_dto(first_name='Novo')
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)

    monkeypatch.setattr(
        employee_postgres_module.EmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _obj: build_employee_dto(first_name='Novo')),
    )

    out = await repository.update_employee(employee_dto.id, payload)

    assert out.first_name == 'Novo'


@pytest.mark.asyncio
async def test_update_employee_integrity_non_unique_raises_database(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
) -> None:
    payload = build_employee_update_dto(first_name='X')
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())

    with pytest.raises(DatabaseException):
        await repository.update_employee(employee_dto.id, payload)


@pytest.mark.asyncio
async def test_update_employee_execute_sqlalchemy_error(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
) -> None:
    payload = build_employee_update_dto(first_name='X')
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.update_employee(employee_dto.id, payload)


@pytest.mark.asyncio
async def test_update_employee_no_row_raises(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
) -> None:
    payload = build_employee_update_dto(first_name='X')
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(DatabaseException, match='Employee not found'):
        await repository.update_employee(employee_dto.id, payload)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_employee_commit_duplicate_raises(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    employee_dto,
) -> None:
    payload = build_employee_update_dto(first_name='X')
    row = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=row)
    mock_session.execute = AsyncMock(return_value=result_mock)
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())

    with pytest.raises(DuplicatedException):
        await repository.update_employee(employee_dto.id, payload)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_employee_success(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
) -> None:
    await repository.delete_employee(uuid4())

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_employee_sqlalchemy_error(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
) -> None:
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.delete_employee(uuid4())


@pytest.mark.asyncio
async def test_list_employee_success(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = MagicMock()
    scalars = MagicMock()
    scalars.all = MagicMock(return_value=[row])
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=scalars)
    mock_session.execute = AsyncMock(return_value=result_mock)

    monkeypatch.setattr(
        employee_postgres_module.EmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _obj: build_employee_dto()),
    )

    out = await repository.list_employee()

    assert len(out) == 1


@pytest.mark.asyncio
async def test_list_employee_sqlalchemy_error(
    repository: EmployeeRepositoryPostgres,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.list_employee()
