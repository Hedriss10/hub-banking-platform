from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoanOperationCreateSchema(BaseModel):
    name: str
    model_config = ConfigDict(str_strip_whitespace=True)


class LoanOperationUpdateSchema(BaseModel):
    name: str
    model_config = ConfigDict(str_strip_whitespace=True)


class LoanOperationOutSchema(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID
