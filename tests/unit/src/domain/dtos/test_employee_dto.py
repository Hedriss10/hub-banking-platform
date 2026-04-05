import pytest
from src.domain.dtos.employee import EmployeeDTO
from src.domain.enum.employee_role import EmployeeRole
from src.infrastructure.database.models.common.role import RoleStatus
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit


def test_employee_dto_role_coerces_role_status() -> None:
    data = build_employee_dto().model_dump()
    data['role'] = RoleStatus.ADMIN
    dto = EmployeeDTO.model_validate(data)
    assert dto.role == EmployeeRole.ADMIN


def test_employee_dto_role_accepts_string_admin() -> None:
    data = build_employee_dto().model_dump()
    data['role'] = 'EMPLOYEE'
    dto = EmployeeDTO.model_validate(data)
    assert dto.role == EmployeeRole.EMPLOYEE


def test_employee_dto_role_keeps_employee_role() -> None:
    dto = build_employee_dto(role=EmployeeRole.ADMIN)
    again = EmployeeDTO.model_validate(dto.model_dump())
    assert again.role == EmployeeRole.ADMIN
