from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from src.domain.enum.employee_role import EmployeeRole


class EmployeeCreateSchema(BaseModel):
    first_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ]
    last_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ] = Field(
        description='Sobrenome',
    )
    document: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=11,
            max_length=14,
            pattern=r'^[\d.\-\s]+$',
        ),
    ] = Field(description='CPF/documento')
    email: Annotated[EmailStr, StringConstraints(strip_whitespace=True, max_length=320)]
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )
    role: EmployeeRole


class EmployeeUpdateSchema(BaseModel):
    first_name: Optional[
        Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
        ]
    ] = None
    last_name: Optional[
        Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
        ]
    ] = None
    document: Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                min_length=11,
                max_length=14,
                pattern=r'^[\d.\-\s]+$',
            ),
        ]
    ] = None
    email: Optional[
        Annotated[EmailStr, StringConstraints(strip_whitespace=True, max_length=320)]
    ] = None
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
    )
    role: Optional[EmployeeRole] = None


class EmployeeSchema(BaseModel):
    id: UUID = Field(..., description='ID')
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    document: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=320)
    role: EmployeeRole = Field(...)
    created_at: datetime
    updated_at: datetime
