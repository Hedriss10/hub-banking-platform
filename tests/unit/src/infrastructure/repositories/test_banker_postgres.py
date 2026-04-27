from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import src.infrastructure.repositories.banker_postgres as banker_postgres_mod
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.bankers import BankerCreateDto, BankerUpdateDto
from src.infrastructure.repositories.banker_postgres import BankersPostgresRepository
from tests.fixtures.banker_factories import build_banker_out_dto

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
def repository(mock_session: AsyncMock) -> BankersPostgresRepository:
    return BankersPostgresRepository(mock_session)


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


@pytest.mark.asyncio
async def test_list_bankers_success(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(
        return_value=_mock_result_with_scalars_all([MagicMock()])
    )
    monkeypatch.setattr(
        banker_postgres_mod.BankerOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: build_banker_out_dto(name='A')),
    )

    out = await repository.list_bankers()
    assert len(out) == 1


@pytest.mark.asyncio
async def test_list_bankers_sqlalchemy_error(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.list_bankers()

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_banker_success(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(MagicMock()))
    monkeypatch.setattr(
        banker_postgres_mod.BankerOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: build_banker_out_dto()),
    )

    out = await repository.get_banker(uuid4())
    assert out is not None


@pytest.mark.asyncio
async def test_get_banker_none(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_with_scalar(None))

    assert await repository.get_banker(uuid4()) is None


@pytest.mark.asyncio
async def test_get_banker_sqlalchemy_error(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.get_banker(uuid4())


@pytest.mark.asyncio
async def test_create_banker_success(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = BankerCreateDto(name='Bco', created_by=uuid4())
    out_dto = build_banker_out_dto(name='Bco')
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    monkeypatch.setattr(
        banker_postgres_mod.BankerOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.create_banker(dto)

    assert out == out_dto
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_banker_integrity_unique(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = BankerCreateDto(name='Bco', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())
    mock_session.add = MagicMock()

    with pytest.raises(DuplicatedException):
        await repository.create_banker(dto)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_banker_integrity_other(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = BankerCreateDto(name='Bco', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())
    mock_session.add = MagicMock()

    with pytest.raises(DatabaseException):
        await repository.create_banker(dto)


@pytest.mark.asyncio
async def test_create_banker_sqlalchemy_error(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    dto = BankerCreateDto(name='Bco', created_by=uuid4())
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))
    mock_session.add = MagicMock()

    with pytest.raises(DatabaseException):
        await repository.create_banker(dto)


@pytest.mark.asyncio
async def test_update_banker_empty_payload_uses_get(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    b = build_banker_out_dto()
    mock_dto = MagicMock()
    mock_dto.model_dump = MagicMock(return_value={})
    monkeypatch.setattr(
        repository,
        'get_banker',
        AsyncMock(return_value=b),
    )

    out = await repository.update_banker(b.id, mock_dto)  # type: ignore[arg-type]

    assert out == b
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_update_banker_with_returning(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    b = build_banker_out_dto(name='Novo')
    row = MagicMock()
    r2 = _mock_result_with_scalar(row)
    mock_session.execute = AsyncMock(return_value=r2)
    mock_session.commit = AsyncMock()
    monkeypatch.setattr(
        banker_postgres_mod.BankerOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: b),
    )

    out = await repository.update_banker(b.id, BankerUpdateDto(name='Novo'))
    assert out.name == 'Novo'


@pytest.mark.asyncio
async def test_update_banker_no_row_from_returning(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    r2 = _mock_result_with_scalar(None)
    mock_session.execute = AsyncMock(return_value=r2)
    mock_session.commit = AsyncMock()

    out = await repository.update_banker(uuid4(), BankerUpdateDto(name='Novo'))
    assert out is None


@pytest.mark.asyncio
async def test_update_banker_integrity_unique(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    r2 = _mock_result_with_scalar(MagicMock())
    mock_session.execute = AsyncMock(return_value=r2)
    mock_session.commit = AsyncMock(side_effect=_integrity_unique())

    with pytest.raises(DuplicatedException):
        await repository.update_banker(uuid4(), BankerUpdateDto(name='Novo'))


@pytest.mark.asyncio
async def test_update_banker_integrity_fk(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    r2 = _mock_result_with_scalar(MagicMock())
    mock_session.execute = AsyncMock(return_value=r2)
    mock_session.commit = AsyncMock(side_effect=_integrity_fk())

    with pytest.raises(DatabaseException):
        await repository.update_banker(uuid4(), BankerUpdateDto(name='Novo'))


@pytest.mark.asyncio
async def test_update_banker_sqlalchemy(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('db'))

    with pytest.raises(DatabaseException):
        await repository.update_banker(uuid4(), BankerUpdateDto(name='Novo'))


@pytest.mark.asyncio
async def test_delete_banker(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    await repository.delete_banker(uuid4())

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_banker_sqlalchemy(
    repository: BankersPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(side_effect=SQLAlchemyError('x'))

    with pytest.raises(DatabaseException):
        await repository.delete_banker(uuid4())

    mock_session.rollback.assert_awaited_once()
