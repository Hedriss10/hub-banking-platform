from unittest.mock import AsyncMock

import pytest
from src.domain.enum.employee_role import EmployeeRole
from src.interface.api.v2.controller.employee import (
    EmployeeController,
    _employee_dto_to_schema,
)
from src.interface.api.v2.schemas.employee import (
    EmployeeCreateSchema,
    EmployeeSchema,
    EmployeeUpdateSchema,
)
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit


def test_employee_dto_to_schema_maps_fields() -> None:
    dto = build_employee_dto()
    schema = _employee_dto_to_schema(dto)
    assert isinstance(schema, EmployeeSchema)
    assert schema.id == dto.id
    assert schema.email == dto.email
    assert schema.role == dto.role


@pytest.mark.asyncio
async def test_create_employee(employee_create_dto) -> None:
    created = build_employee_dto(email=employee_create_dto.email)
    use_case = AsyncMock()
    use_case.create_employee = AsyncMock(return_value=created)
    controller = EmployeeController(use_case)

    body = EmployeeCreateSchema.model_validate(employee_create_dto.model_dump())
    result = await controller.create_employee(body)

    assert isinstance(result, EmployeeSchema)
    use_case.create_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_employee(employee_dto) -> None:
    use_case = AsyncMock()
    use_case.list_employee = AsyncMock(return_value=[employee_dto])
    controller = EmployeeController(use_case)

    rows = await controller.list_employee()

    assert len(rows) == 1
    assert rows[0].id == employee_dto.id


@pytest.mark.asyncio
async def test_get_employee(employee_dto, random_employee_id) -> None:
    use_case = AsyncMock()
    use_case.get_employee = AsyncMock(return_value=employee_dto)
    controller = EmployeeController(use_case)

    result = await controller.get_employee(random_employee_id)

    assert result.id == employee_dto.id


@pytest.mark.asyncio
async def test_update_employee(employee_dto, random_employee_id) -> None:
    updated = build_employee_dto(first_name='New')
    use_case = AsyncMock()
    use_case.update_employee = AsyncMock(return_value=updated)
    controller = EmployeeController(use_case)

    patch = EmployeeUpdateSchema(first_name='New', role=EmployeeRole.ADMIN)
    result = await controller.update_employee(random_employee_id, patch)

    assert result.first_name == 'New'
    use_case.update_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_employee(random_employee_id) -> None:
    use_case = AsyncMock()
    use_case.delete_employee = AsyncMock(return_value=None)
    controller = EmployeeController(use_case)

    await controller.delete_employee(random_employee_id)

    use_case.delete_employee.assert_awaited_once_with(random_employee_id)
