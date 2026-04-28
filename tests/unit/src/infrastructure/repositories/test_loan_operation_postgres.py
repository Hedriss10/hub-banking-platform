from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import src.infrastructure.repositories.loan_operation_postgres as lo_module
from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationUpdateDTO,
)
from src.infrastructure.repositories.loan_operation_postgres import (
    LoanOperationPostgresRepository,
)
from tests.fixtures.loan_operation_factories import build_loan_operation_out_dto

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(mock_session: AsyncMock) -> LoanOperationPostgresRepository:
    return LoanOperationPostgresRepository(mock_session)


def _mock_result_scalar(one: object | None) -> MagicMock:
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=one)
    return result


def _mock_result_scalars_all(rows: list) -> MagicMock:
    scal = MagicMock()
    scal.all = MagicMock(return_value=rows)
    result = MagicMock()
    result.scalars = MagicMock(return_value=scal)
    return result


@pytest.mark.asyncio
async def test_create_loan_operation_success(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = LoanOperationCreateDTO(name='Op', created_by=uuid4())
    out_dto = build_loan_operation_out_dto(name='Op', created_by=dto.created_by)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    monkeypatch.setattr(
        lo_module,
        'LoanOperation',
        MagicMock(side_effect=lambda **_: MagicMock()),
    )
    monkeypatch.setattr(
        lo_module.LoanOperationOutDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.create_loan_operation(dto)

    assert out == out_dto
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_loan_operation_by_id_none(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalar(None))

    assert await repository.get_loan_operation_by_id(uuid4()) is None


@pytest.mark.asyncio
async def test_get_loan_operation_by_id_success(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalar(MagicMock()))
    out_dto = build_loan_operation_out_dto()
    monkeypatch.setattr(
        lo_module.LoanOperationOutDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    row = await repository.get_loan_operation_by_id(out_dto.id)

    assert row == out_dto


@pytest.mark.asyncio
async def test_update_loan_operation_no_row(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get = AsyncMock(return_value=None)

    got = await repository.update_loan_operation(
        uuid4(), LoanOperationUpdateDTO(name='X')
    )

    assert got is None


@pytest.mark.asyncio
async def test_update_loan_operation_deleted_row(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = True
    mock_session.get = AsyncMock(return_value=row)

    got = await repository.update_loan_operation(
        uuid4(), LoanOperationUpdateDTO(name='X')
    )

    assert got is None


@pytest.mark.asyncio
async def test_update_loan_operation_success(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = MagicMock()
    row.is_deleted = False
    row.name = 'Old'
    out_dto = build_loan_operation_out_dto(name='New')

    mock_session.get = AsyncMock(return_value=row)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    monkeypatch.setattr(
        lo_module.LoanOperationOutDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    data = LoanOperationUpdateDTO(name='New')
    got = await repository.update_loan_operation(uuid4(), data)

    assert got == out_dto
    assert row.name == 'New'


@pytest.mark.asyncio
async def test_delete_loan_operation_no_row(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get = AsyncMock(return_value=None)

    await repository.delete_loan_operation(uuid4())

    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_loan_operation_already_deleted(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = True
    mock_session.get = AsyncMock(return_value=row)

    await repository.delete_loan_operation(uuid4())

    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_loan_operation_soft_delete(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = False
    mock_session.get = AsyncMock(return_value=row)
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    await repository.delete_loan_operation(uuid4())

    assert row.is_deleted is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_loan_operations_empty(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalars_all([]))

    out = await repository.list_loan_operations()

    assert out == []


@pytest.mark.asyncio
async def test_list_loan_operations_rows(
    repository: LoanOperationPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(
        return_value=_mock_result_scalars_all([MagicMock()])
    )
    out_dto = build_loan_operation_out_dto()

    monkeypatch.setattr(
        lo_module.LoanOperationOutDTO,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.list_loan_operations()

    assert len(out) == 1
    assert out[0] == out_dto
