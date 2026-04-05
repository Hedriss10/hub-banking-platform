from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.enum.employee_role import EmployeeRole


class EmployeeCreateSchema(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
        description='Sobrenome (coluna `last_name`, String NOT NULL)',
    )
    document: str = Field(
        ...,
        min_length=11,
        max_length=14,
        pattern=r'^[\d.\-\s]+$',
        strip_whitespace=True,
        description='CPF/documento (coluna `document`, String NOT NULL, UNIQUE)',
    )
    email: EmailStr = Field(
        ...,
        max_length=320,
        strip_whitespace=True,
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )
    role: EmployeeRole


class EmployeeUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
    )
    document: Optional[str] = Field(
        None,
        min_length=11,
        max_length=14,
        pattern=r'^[\d.\-\s]+$',
        strip_whitespace=True,
    )
    email: Optional[EmailStr] = Field(None, max_length=320, strip_whitespace=True)
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
    )
    role: Optional[EmployeeRole] = None


class EmployeeSchema(BaseModel):
    """Resposta alinhada às colunas lidas do modelo (password pode ser hash longo)."""

    id: UUID = Field(..., description='PK')
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    document: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=320)
    role: EmployeeRole = Field(...)
    created_at: datetime
    updated_at: datetime
