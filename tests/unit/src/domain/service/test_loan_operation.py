from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationUpdateDTO,
)
from src.domain.service.loan_operation import LoanOperationService
from tests.fixtures.loan_operation_factories import build_loan_operation_out_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_loan_operation_delegates() -> None:
    dto = LoanOperationCreateDTO(name='A', created_by=uuid4())
    out = build_loan_operation_out_dto()
    repo = AsyncMock()
    repo.create_loan_operation = AsyncMock(return_value=out)
    service = LoanOperationService(repo)

    result = await service.create_loan_operation(dto)

    assert result == out
    repo.create_loan_operation.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_get_loan_operation_by_id_delegates() -> None:
    eid = uuid4()
    out = build_loan_operation_out_dto()
    repo = AsyncMock()
    repo.get_loan_operation_by_id = AsyncMock(return_value=out)
    service = LoanOperationService(repo)

    result = await service.get_loan_operation_by_id(eid)

    assert result == out
    repo.get_loan_operation_by_id.assert_awaited_once_with(eid)


@pytest.mark.asyncio
async def test_update_loan_operation_delegates() -> None:
    eid = uuid4()
    data = LoanOperationUpdateDTO(name='X')
    out = build_loan_operation_out_dto()
    repo = AsyncMock()
    repo.update_loan_operation = AsyncMock(return_value=out)
    service = LoanOperationService(repo)

    result = await service.update_loan_operation(eid, data)

    assert result == out
    repo.update_loan_operation.assert_awaited_once_with(eid, data)


@pytest.mark.asyncio
async def test_delete_loan_operation_delegates() -> None:
    eid = uuid4()
    repo = AsyncMock()
    repo.delete_loan_operation = AsyncMock(return_value=None)
    service = LoanOperationService(repo)

    await service.delete_loan_operation(eid)

    repo.delete_loan_operation.assert_awaited_once_with(eid)


@pytest.mark.asyncio
async def test_list_loan_operations_delegates() -> None:
    rows = [build_loan_operation_out_dto()]
    repo = AsyncMock()
    repo.list_loan_operations = AsyncMock(return_value=rows)
    service = LoanOperationService(repo)

    result = await service.list_loan_operations()

    assert result == rows
    repo.list_loan_operations.assert_awaited_once_with()
