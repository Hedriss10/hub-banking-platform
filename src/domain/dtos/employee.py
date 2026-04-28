from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.enum.employee_role import EmployeeRole


def _to_employee_role(value: Any) -> EmployeeRole:
    if isinstance(value, EmployeeRole):
        return value
    if isinstance(value, Enum):
        return EmployeeRole(value.value)
    return EmployeeRole(value)


class EmployeeCreateDTO(BaseModel):
    first_name: str
    last_name: str
    document: str
    email: str
    password: str
    role: EmployeeRole


class EmployeeUpdateDTO(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    document: Optional[str] = None
    email: Optional[str] = None
    role: Optional[EmployeeRole] = None


class EmployeeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    document: str
    email: str
    password: str
    role: EmployeeRole
    created_at: datetime
    updated_at: datetime

    @field_validator('role', mode='before')
    @classmethod
    def role_from_orm(cls, value: Any) -> EmployeeRole:
        """Maps ORM ``RoleStatus`` to domain ``EmployeeRole`` (same values)."""
        return _to_employee_role(value)
