from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import src.infrastructure.repositories.rooms_postgres as rooms_postgres_mod
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.rooms import RoomCreateDTO, RoomUpdateDTO
from src.domain.dtos.rooms_employee import RoomEmployeeCreateDTO
from src.infrastructure.repositories.rooms_postgres import RoomsPostgresRepository
from tests.fixtures.room_factories import build_room_dto, build_room_employee_dto

pytestmark = pytest.mark.unit


def _integrity_unique() -> IntegrityError:
    orig = MagicMock()
    orig.pgcode = '23505'
    return IntegrityError('stmt', None, orig)


def _integrity_fk() -> IntegrityError:
    orig = MagicMock()
    orig.pgcode = '23503'
    return IntegrityError('stmt', None, orig)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(mock_session: AsyncMock) -> RoomsPostgresRepository:
    return RoomsPostgresRepository(mock_session)


def _mock_result_with_scalar(value: object | None) -> MagicMock:
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=value)
    return result


def _mock_result_with_scalars_all(rows: list) -> MagicMock:
    scal = MagicMock()
    scal.all = MagicMock(return_value=rows)
    result = MagicMock()
    result.scalars = MagicMock(return_value=scal)
    return result


def _mock_execute_result_with_rowcount(n: int) -> MagicMock:
    result = MagicMock()
    result.rowcount = n
    return result


def _mock_result_with_all(rows: list) -> MagicMock:
    result = MagicMock()
    result.all = MagicMock(return_value=rows)
    return result


@pytest.mark.asyncio
async def test_get_room_by_id_success(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(MagicMock()))
    monkeypatch.setattr(
        rooms_postgres_mod.RoomDTO,
        'model_validate',
        classmethod(lambda _cls, _o: build_room_dto()),
    )

    out = await repository.get_room_by_id(uuid4())
    assert out is not None


@pytest.mark.asyncio
async def test_get_room_by_id_none(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(None))
    assert await repository.get_room_by_id(uuid4()) is None


@pytest.mark.asyncio
async def test_get_room_by_id_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))
    with pytest.raises(DatabaseException):
        await repository.get_room_by_id(uuid4())
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_rooms_success(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(
        return_value=_mock_result_with_scalars_all([MagicMock()]),
    )
    monkeypatch.setattr(
        rooms_postgres_mod.RoomDTO,
        'model_validate',
        classmethod(lambda _cls, _o: build_room_dto(name='A')),
    )
    out = await repository.get_all_rooms()
    assert len(out) == 1


@pytest.mark.asyncio
async def test_get_all_rooms_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))
    with pytest.raises(DatabaseException):
        await repository.get_all_rooms()


@pytest.mark.asyncio
async def test_create_room_success(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = RoomCreateDTO(name='R1', created_by=uuid4())
    out_dto = build_room_dto(name='R1')
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    monkeypatch.setattr(
        rooms_postgres_mod.RoomDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.create_room(dto)
    assert out == out_dto
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_room_integrity_unique(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = RoomCreateDTO(name='R1', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())
    mock_session.add = MagicMock()
    with pytest.raises(DuplicatedException):
        await repository.create_room(dto)
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_room_integrity_other(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = RoomCreateDTO(name='R1', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())
    mock_session.add = MagicMock()
    with pytest.raises(DatabaseException):
        await repository.create_room(dto)


@pytest.mark.asyncio
async def test_create_room_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = RoomCreateDTO(name='R1', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))
    mock_session.add = MagicMock()
    with pytest.raises(DatabaseException):
        await repository.create_room(dto)


@pytest.mark.asyncio
async def test_update_room_empty_payload_uses_get(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    r = build_room_dto()
    mock_payload = MagicMock()
    mock_payload.model_dump = MagicMock(return_value={})
    monkeypatch.setattr(
        repository,
        'get_room_by_id',
        AsyncMock(return_value=r),
    )
    out = await repository.update_room(r.id, mock_payload)  # type: ignore[arg-type]
    assert out == r


@pytest.mark.asyncio
async def test_update_room_with_returning(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    r = build_room_dto(name='Novo')
    row = MagicMock()
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(row))
    mock_session.commit = AsyncMock()
    monkeypatch.setattr(
        rooms_postgres_mod.RoomDTO,
        'model_validate',
        classmethod(lambda _cls, _o: r),
    )
    out = await repository.update_room(r.id, RoomUpdateDTO(name='Novo'))
    assert out.name == 'Novo'


@pytest.mark.asyncio
async def test_update_room_no_row_from_returning(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(None))
    mock_session.commit = AsyncMock()
    out = await repository.update_room(uuid4(), RoomUpdateDTO(name='Novo'))
    assert out is None


@pytest.mark.asyncio
async def test_update_room_integrity_unique(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(MagicMock()))
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())
    with pytest.raises(DuplicatedException):
        await repository.update_room(uuid4(), RoomUpdateDTO(name='Novo'))


@pytest.mark.asyncio
async def test_update_room_integrity_non_unique_raises_database(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(MagicMock()))
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())
    with pytest.raises(DatabaseException):
        await repository.update_room(uuid4(), RoomUpdateDTO(name='Novo'))


@pytest.mark.asyncio
async def test_update_room_sqlalchemy_on_execute(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))
    with pytest.raises(DatabaseException):
        await repository.update_room(uuid4(), RoomUpdateDTO(name='Novo'))


@pytest.mark.asyncio
async def test_delete_room_commits_when_rows(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_execute_result_with_rowcount(1))
    mock_session.commit = AsyncMock()

    await repository.delete_room(uuid4())

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room_rollbacks_when_zero_rows(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_execute_result_with_rowcount(0))

    await repository.delete_room(uuid4())

    mock_session.rollback.assert_awaited_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_room_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('x'))
    with pytest.raises(DatabaseException):
        await repository.delete_room(uuid4())
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_room_employee_success(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = RoomEmployeeCreateDTO(room_id=uuid4(), employee_id=uuid4())
    out_dto = build_room_employee_dto(
        room_id=dto.room_id,
        employee_id=dto.employee_id,
    )
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    monkeypatch.setattr(
        rooms_postgres_mod.RoomEmployeeDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.create_room_employee(dto)

    assert out == out_dto
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_room_employee_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = RoomEmployeeCreateDTO(room_id=uuid4(), employee_id=uuid4())
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))
    mock_session.add = MagicMock()

    with pytest.raises(DatabaseException):
        await repository.create_room_employee(dto)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_room_employees_success(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    rooms_employee = MagicMock()
    rooms_employee.id = uuid4()
    rooms_employee.room_id = uuid4()
    rooms_employee.employee_id = uuid4()
    mock_session.execute = AsyncMock(
        return_value=_mock_result_with_all([(rooms_employee, 'Maria', 'Silva')]),
    )

    out = await repository.get_room_employees(rooms_employee.room_id)

    assert len(out) == 1
    assert out[0].first_name == 'Maria'
    assert out[0].last_name == 'Silva'
    assert out[0].employee_id == rooms_employee.employee_id


@pytest.mark.asyncio
async def test_get_room_employees_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.get_room_employees(uuid4())

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room_employee_commits_when_rows(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_execute_result_with_rowcount(1))
    mock_session.commit = AsyncMock()

    await repository.delete_room_employee(uuid4(), uuid4())

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room_employee_rollbacks_when_zero_rows(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_execute_result_with_rowcount(0))

    await repository.delete_room_employee(uuid4(), uuid4())

    mock_session.rollback.assert_awaited_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_room_employee_sqlalchemy_error(
    repository: RoomsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('x'))

    with pytest.raises(DatabaseException):
        await repository.delete_room_employee(uuid4(), uuid4())

    mock_session.rollback.assert_awaited_once()
