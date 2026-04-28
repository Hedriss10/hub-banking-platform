from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoanOperationCreateDTO(BaseModel):
    name: str
    created_by: UUID
    model_config = ConfigDict(str_strip_whitespace=True)


class LoanOperationUpdateDTO(BaseModel):
    name: str
    model_config = ConfigDict(str_strip_whitespace=True)


class LoanOperationOutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID
