"""Testes do serviço Employee — delegação ao repositório."""

from unittest.mock import AsyncMock

import pytest
from src.domain.service.employee import EmployeeService
from tests.fixtures.employee_factories import (
    build_employee_dto,
    build_employee_update_dto,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_employee_delegates(employee_create_dto) -> None:
    expected = build_employee_dto(email=employee_create_dto.email)
    repo = AsyncMock()
    repo.create_employee = AsyncMock(return_value=expected)
    service = EmployeeService(repo)

    result = await service.create_employee(employee_create_dto)

    assert result == expected
    repo.create_employee.assert_awaited_once_with(employee_create_dto)


@pytest.mark.asyncio
async def test_get_employee_delegates(random_employee_id, employee_dto) -> None:
    repo = AsyncMock()
    repo.get_employee_by_id = AsyncMock(return_value=employee_dto)
    service = EmployeeService(repo)

    result = await service.get_employee(random_employee_id)

    assert result == employee_dto
    repo.get_employee_by_id.assert_awaited_once_with(random_employee_id)


@pytest.mark.asyncio
async def test_update_employee_delegates(random_employee_id, employee_dto) -> None:
    payload = build_employee_update_dto()
    updated = build_employee_dto(first_name='X')
    repo = AsyncMock()
    repo.update_employee = AsyncMock(return_value=updated)
    service = EmployeeService(repo)

    result = await service.update_employee(random_employee_id, payload)

    assert result == updated
    repo.update_employee.assert_awaited_once_with(random_employee_id, payload)


@pytest.mark.asyncio
async def test_delete_employee_delegates(random_employee_id) -> None:
    repo = AsyncMock()
    repo.delete_employee = AsyncMock(return_value=None)
    service = EmployeeService(repo)

    await service.delete_employee(random_employee_id)

    repo.delete_employee.assert_awaited_once_with(random_employee_id)


@pytest.mark.asyncio
async def test_list_employee_delegates(employee_dto) -> None:
    repo = AsyncMock()
    repo.list_employee = AsyncMock(return_value=[employee_dto])
    service = EmployeeService(repo)

    result = await service.list_employee()

    assert result == [employee_dto]
