from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.service.financial_agreements import FinancialAgreementsService
from tests.fixtures.financial_agreements_factories import (
    build_financial_agreement_out_dto,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_financial_agreement_delegates() -> None:
    dto = FinancialAgreementsCreateDto(
        name='A',
        bankers_id=uuid4(),
        created_by=uuid4(),
    )
    out = build_financial_agreement_out_dto()
    repo = AsyncMock()
    repo.create_financial_agreement = AsyncMock(return_value=out)
    service = FinancialAgreementsService(repo)

    result = await service.create_financial_agreement(dto)

    assert result == out
    repo.create_financial_agreement.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_get_financial_agreement_delegates() -> None:
    eid = uuid4()
    out = build_financial_agreement_out_dto()
    repo = AsyncMock()
    repo.get_financial_agreement = AsyncMock(return_value=out)
    service = FinancialAgreementsService(repo)

    result = await service.get_financial_agreement(eid)

    assert result == out
    repo.get_financial_agreement.assert_awaited_once_with(eid)


@pytest.mark.asyncio
async def test_update_financial_agreement_delegates() -> None:
    eid = uuid4()
    data = FinancialAgreementsUpdateDto(name='X')
    out = build_financial_agreement_out_dto()
    repo = AsyncMock()
    repo.update_financial_agreement = AsyncMock(return_value=out)
    service = FinancialAgreementsService(repo)

    result = await service.update_financial_agreement(eid, data)

    assert result == out
    repo.update_financial_agreement.assert_awaited_once_with(eid, data)


@pytest.mark.asyncio
async def test_delete_financial_agreement_delegates() -> None:
    eid = uuid4()
    repo = AsyncMock()
    repo.delete_financial_agreement = AsyncMock(return_value=None)
    service = FinancialAgreementsService(repo)

    await service.delete_financial_agreement(eid)

    repo.delete_financial_agreement.assert_awaited_once_with(eid)


@pytest.mark.asyncio
async def test_list_financial_agreements_delegates() -> None:
    bank_id = uuid4()
    rows = [build_financial_agreement_out_dto()]
    repo = AsyncMock()
    repo.list_financial_agreements = AsyncMock(return_value=rows)
    service = FinancialAgreementsService(repo)

    result = await service.list_financial_agreements(bank_id)

    assert result == rows
    repo.list_financial_agreements.assert_awaited_once_with(bank_id)
