from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import src.infrastructure.repositories.financial_agreements_postgres as fa_module
from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsUpdateDto,
)
from src.infrastructure.repositories.financial_agreements_postgres import (
    FinancialAgreementsPostgresRepository,
)
from tests.fixtures.financial_agreements_factories import (
    build_financial_agreement_out_dto,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(mock_session: AsyncMock) -> FinancialAgreementsPostgresRepository:
    return FinancialAgreementsPostgresRepository(mock_session)


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
async def test_create_financial_agreement_success(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto = FinancialAgreementsCreateDto(
        name='Agree',
        bankers_id=uuid4(),
        created_by=uuid4(),
    )
    out_dto = build_financial_agreement_out_dto(name='Agree', bankers_id=dto.bankers_id)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    monkeypatch.setattr(
        fa_module,
        'FinancialAgreementsModel',
        MagicMock(side_effect=lambda **_: MagicMock()),
    )
    monkeypatch.setattr(
        fa_module.FinancialAgreementsOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.create_financial_agreement(dto)

    assert out == out_dto
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_financial_agreement_none(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalar(None))

    assert await repository.get_financial_agreement(uuid4()) is None


@pytest.mark.asyncio
async def test_get_financial_agreement_success(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalar(MagicMock()))
    out_dto = build_financial_agreement_out_dto()
    monkeypatch.setattr(
        fa_module.FinancialAgreementsOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    row = await repository.get_financial_agreement(out_dto.id)

    assert row == out_dto


@pytest.mark.asyncio
async def test_update_financial_agreement_no_row(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get = AsyncMock(return_value=None)

    got = await repository.update_financial_agreement(
        uuid4(), FinancialAgreementsUpdateDto(name='X')
    )

    assert got is None


@pytest.mark.asyncio
async def test_update_financial_agreement_deleted_row(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = True
    mock_session.get = AsyncMock(return_value=row)

    got = await repository.update_financial_agreement(
        uuid4(), FinancialAgreementsUpdateDto(name='X')
    )

    assert got is None


@pytest.mark.asyncio
async def test_update_financial_agreement_success(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = MagicMock()
    row.is_deleted = False
    row.name = 'Old'
    out_dto = build_financial_agreement_out_dto(name='New')

    mock_session.get = AsyncMock(return_value=row)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    monkeypatch.setattr(
        fa_module.FinancialAgreementsOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    data = FinancialAgreementsUpdateDto(name='New')
    got = await repository.update_financial_agreement(uuid4(), data)

    assert got == out_dto
    assert row.name == 'New'


@pytest.mark.asyncio
async def test_delete_financial_agreement_no_row(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get = AsyncMock(return_value=None)

    await repository.delete_financial_agreement(uuid4())

    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_financial_agreement_already_deleted(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = True
    mock_session.get = AsyncMock(return_value=row)

    await repository.delete_financial_agreement(uuid4())

    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_financial_agreement_soft_delete(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    row = MagicMock()
    row.is_deleted = False
    mock_session.get = AsyncMock(return_value=row)
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    await repository.delete_financial_agreement(uuid4())

    assert row.is_deleted is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_financial_agreements_empty(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.execute = AsyncMock(return_value=_mock_result_scalars_all([]))

    out = await repository.list_financial_agreements(uuid4())

    assert out == []


@pytest.mark.asyncio
async def test_list_financial_agreements_rows(
    repository: FinancialAgreementsPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.execute = AsyncMock(
        return_value=_mock_result_scalars_all([MagicMock()])
    )
    out_dto = build_financial_agreement_out_dto()

    monkeypatch.setattr(
        fa_module.FinancialAgreementsOutDto,
        'model_validate',
        classmethod(lambda _cls, _o: out_dto),
    )

    out = await repository.list_financial_agreements(uuid4())

    assert len(out) == 1
    assert out[0] == out_dto
