from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.exceptions.financial_agreements import (
    FinancialAgreementNotFoundException,
)
from src.domain.use_case.financial_agreements import FinancialAgreementsUseCase
from tests.fixtures.financial_agreements_factories import (
    build_financial_agreement_out_dto,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_financial_agreement() -> None:
    dto = FinancialAgreementsCreateDto(
        name='A',
        bankers_id=uuid4(),
        created_by=uuid4(),
    )
    created = build_financial_agreement_out_dto()
    service = AsyncMock()
    service.create_financial_agreement = AsyncMock(return_value=created)
    uc = FinancialAgreementsUseCase(service)

    out = await uc.create_financial_agreement(dto)

    assert out == created
    service.create_financial_agreement.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_list_financial_agreements() -> None:
    bank_id = uuid4()
    items = [build_financial_agreement_out_dto()]
    service = AsyncMock()
    service.list_financial_agreements = AsyncMock(return_value=items)
    uc = FinancialAgreementsUseCase(service)

    result = await uc.list_financial_agreements(bank_id)

    assert result == items


@pytest.mark.asyncio
async def test_get_financial_agreement_success() -> None:
    fa = build_financial_agreement_out_dto()
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=fa)
    uc = FinancialAgreementsUseCase(service)

    out = await uc.get_financial_agreement(fa.id)

    assert out == fa


@pytest.mark.asyncio
async def test_get_financial_agreement_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=None)
    uc = FinancialAgreementsUseCase(service)

    with pytest.raises(FinancialAgreementNotFoundException, match='not found'):
        await uc.get_financial_agreement(eid)


@pytest.mark.asyncio
async def test_update_financial_agreement_success() -> None:
    fa = build_financial_agreement_out_dto()
    updated = build_financial_agreement_out_dto(name='Renamed')
    data = FinancialAgreementsUpdateDto(name='Renamed')
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=fa)
    service.update_financial_agreement = AsyncMock(return_value=updated)
    uc = FinancialAgreementsUseCase(service)

    out = await uc.update_financial_agreement(fa.id, data)

    assert out == updated


@pytest.mark.asyncio
async def test_update_financial_agreement_not_found_on_get() -> None:
    eid = uuid4()
    data = FinancialAgreementsUpdateDto(name='X')
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=None)
    uc = FinancialAgreementsUseCase(service)

    with pytest.raises(FinancialAgreementNotFoundException):
        await uc.update_financial_agreement(eid, data)


@pytest.mark.asyncio
async def test_update_financial_agreement_not_found_after_update() -> None:
    fa = build_financial_agreement_out_dto()
    data = FinancialAgreementsUpdateDto(name='X')
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=fa)
    service.update_financial_agreement = AsyncMock(return_value=None)
    uc = FinancialAgreementsUseCase(service)

    with pytest.raises(FinancialAgreementNotFoundException):
        await uc.update_financial_agreement(fa.id, data)


@pytest.mark.asyncio
async def test_delete_financial_agreement() -> None:
    fa = build_financial_agreement_out_dto()
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=fa)
    service.delete_financial_agreement = AsyncMock(return_value=None)
    uc = FinancialAgreementsUseCase(service)

    await uc.delete_financial_agreement(fa.id)

    service.delete_financial_agreement.assert_awaited_once_with(fa.id)


@pytest.mark.asyncio
async def test_delete_financial_agreement_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_financial_agreement = AsyncMock(return_value=None)
    uc = FinancialAgreementsUseCase(service)

    with pytest.raises(FinancialAgreementNotFoundException):
        await uc.delete_financial_agreement(eid)
