"""Testes do caso de uso Employee (exceções de domínio e orquestração)."""

from unittest.mock import AsyncMock

import pytest
from src.core.exceptions.custom import DuplicatedException
from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeUpdateDTO
from src.domain.exceptions.employee import (
    EmployeeAlreadyExistsException,
    EmployeeNotFoundException,
)
from src.domain.use_case.employee import EmployeeUseCase
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_employee_success(employee_create_dto: EmployeeCreateDTO) -> None:
    expected = build_employee_dto(email=employee_create_dto.email)
    service = AsyncMock()
    service.create_employee = AsyncMock(return_value=expected)
    use_case = EmployeeUseCase(service)

    result = await use_case.create_employee(employee_create_dto)

    assert result == expected
    service.create_employee.assert_awaited_once_with(employee_create_dto)


@pytest.mark.asyncio
async def test_create_employee_maps_duplicated_exception(
    employee_create_dto: EmployeeCreateDTO,
) -> None:
    service = AsyncMock()
    service.create_employee = AsyncMock(side_effect=DuplicatedException('unique'))
    use_case = EmployeeUseCase(service)

    with pytest.raises(EmployeeAlreadyExistsException):
        await use_case.create_employee(employee_create_dto)


@pytest.mark.asyncio
async def test_get_employee_success(employee_dto, random_employee_id) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=employee_dto)
    use_case = EmployeeUseCase(service)

    result = await use_case.get_employee(random_employee_id)

    assert result == employee_dto


@pytest.mark.asyncio
async def test_get_employee_not_found(random_employee_id) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=None)
    use_case = EmployeeUseCase(service)

    with pytest.raises(EmployeeNotFoundException):
        await use_case.get_employee(random_employee_id)


@pytest.mark.asyncio
async def test_update_employee_success(
    employee_dto,
    random_employee_id,
    employee_update_dto: EmployeeUpdateDTO,
) -> None:
    updated = build_employee_dto(first_name='Updated')
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=employee_dto)
    service.update_employee = AsyncMock(return_value=updated)
    use_case = EmployeeUseCase(service)

    result = await use_case.update_employee(random_employee_id, employee_update_dto)

    assert result == updated


@pytest.mark.asyncio
async def test_update_employee_not_found(
    random_employee_id,
    employee_update_dto: EmployeeUpdateDTO,
) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=None)
    use_case = EmployeeUseCase(service)

    with pytest.raises(EmployeeNotFoundException):
        await use_case.update_employee(random_employee_id, employee_update_dto)


@pytest.mark.asyncio
async def test_update_employee_maps_duplicated_exception(
    employee_dto,
    random_employee_id,
    employee_update_dto: EmployeeUpdateDTO,
) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=employee_dto)
    service.update_employee = AsyncMock(side_effect=DuplicatedException('unique'))
    use_case = EmployeeUseCase(service)

    with pytest.raises(EmployeeAlreadyExistsException):
        await use_case.update_employee(random_employee_id, employee_update_dto)


@pytest.mark.asyncio
async def test_delete_employee_success(employee_dto, random_employee_id) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=employee_dto)
    service.delete_employee = AsyncMock(return_value=None)
    use_case = EmployeeUseCase(service)

    await use_case.delete_employee(random_employee_id)

    service.delete_employee.assert_awaited_once_with(random_employee_id)


@pytest.mark.asyncio
async def test_delete_employee_not_found(random_employee_id) -> None:
    service = AsyncMock()
    service.get_employee = AsyncMock(return_value=None)
    use_case = EmployeeUseCase(service)

    with pytest.raises(EmployeeNotFoundException):
        await use_case.delete_employee(random_employee_id)


@pytest.mark.asyncio
async def test_list_employee_success(employee_dto) -> None:
    service = AsyncMock()
    service.list_employee = AsyncMock(return_value=[employee_dto])
    use_case = EmployeeUseCase(service)

    result = await use_case.list_employee()

    assert result == [employee_dto]
