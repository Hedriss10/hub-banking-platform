"""
Pure factories for employee DTOs — reusable in unit and integration tests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO
from src.domain.enum.employee_role import EmployeeRole


def build_employee_create_dto(
    *,
    first_name: str = 'John',
    last_name: str = 'Doe',
    document: str = '123456789012',
    email: str = 'john@example.com',
    password: str = 'password12',
    role: EmployeeRole = EmployeeRole.EMPLOYEE,
) -> EmployeeCreateDTO:
    return EmployeeCreateDTO(
        first_name=first_name,
        last_name=last_name,
        document=document,
        email=email,
        password=password,
        role=role,
    )


def build_employee_update_dto(
    *,
    first_name: str | None = 'Jane',
    last_name: str | None = None,
    document: str | None = None,
    email: str | None = None,
    role: EmployeeRole | None = None,
) -> EmployeeUpdateDTO:
    return EmployeeUpdateDTO(
        first_name=first_name,
        last_name=last_name,
        document=document,
        email=email,
        role=role,
    )


def build_employee_dto(
    *,
    id: UUID | None = None,
    first_name: str = 'John',
    last_name: str = 'Doe',
    document: str = '123456789012',
    email: str = 'john@example.com',
    password: str = 'hashed',
    role: EmployeeRole = EmployeeRole.ADMIN,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> EmployeeDTO:
    now = datetime.now(timezone.utc)
    return EmployeeDTO(
        id=id or uuid4(),
        first_name=first_name,
        last_name=last_name,
        document=document,
        email=email,
        password=password,
        role=role,
        created_at=created_at or now,
        updated_at=updated_at or now,
    )
