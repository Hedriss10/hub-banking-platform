from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationUpdateDTO,
)
from src.domain.exceptions.loan_operation import LoanOperationNotFoundException
from src.domain.use_case.loan_operation import LoanOperationUseCase
from tests.fixtures.loan_operation_factories import build_loan_operation_out_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_loan_operation() -> None:
    dto = LoanOperationCreateDTO(name='A', created_by=uuid4())
    created = build_loan_operation_out_dto()
    service = AsyncMock()
    service.create_loan_operation = AsyncMock(return_value=created)
    uc = LoanOperationUseCase(service)

    out = await uc.create_loan_operation(dto)

    assert out == created
    service.create_loan_operation.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_list_loan_operations() -> None:
    items = [build_loan_operation_out_dto()]
    service = AsyncMock()
    service.list_loan_operations = AsyncMock(return_value=items)
    uc = LoanOperationUseCase(service)

    result = await uc.list_loan_operations()

    assert result == items


@pytest.mark.asyncio
async def test_get_loan_operation_success() -> None:
    lo = build_loan_operation_out_dto()
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=lo)
    uc = LoanOperationUseCase(service)

    out = await uc.get_loan_operation(lo.id)

    assert out == lo


@pytest.mark.asyncio
async def test_get_loan_operation_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=None)
    uc = LoanOperationUseCase(service)

    with pytest.raises(LoanOperationNotFoundException, match='not found'):
        await uc.get_loan_operation(eid)


@pytest.mark.asyncio
async def test_update_loan_operation_success() -> None:
    lo = build_loan_operation_out_dto()
    updated = build_loan_operation_out_dto(name='Renamed', id=lo.id)
    data = LoanOperationUpdateDTO(name='Renamed')
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=lo)
    service.update_loan_operation = AsyncMock(return_value=updated)
    uc = LoanOperationUseCase(service)

    out = await uc.update_loan_operation(lo.id, data)

    assert out == updated


@pytest.mark.asyncio
async def test_update_loan_operation_not_found_on_get() -> None:
    eid = uuid4()
    data = LoanOperationUpdateDTO(name='X')
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=None)
    uc = LoanOperationUseCase(service)

    with pytest.raises(LoanOperationNotFoundException):
        await uc.update_loan_operation(eid, data)


@pytest.mark.asyncio
async def test_update_loan_operation_not_found_after_update() -> None:
    lo = build_loan_operation_out_dto()
    data = LoanOperationUpdateDTO(name='X')
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=lo)
    service.update_loan_operation = AsyncMock(return_value=None)
    uc = LoanOperationUseCase(service)

    with pytest.raises(LoanOperationNotFoundException):
        await uc.update_loan_operation(lo.id, data)


@pytest.mark.asyncio
async def test_delete_loan_operation() -> None:
    lo = build_loan_operation_out_dto()
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=lo)
    service.delete_loan_operation = AsyncMock(return_value=None)
    uc = LoanOperationUseCase(service)

    await uc.delete_loan_operation(lo.id)

    service.delete_loan_operation.assert_awaited_once_with(lo.id)


@pytest.mark.asyncio
async def test_delete_loan_operation_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_loan_operation_by_id = AsyncMock(return_value=None)
    uc = LoanOperationUseCase(service)

    with pytest.raises(LoanOperationNotFoundException):
        await uc.delete_loan_operation(eid)
