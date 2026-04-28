from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FinancialAgreementsCreateDto(BaseModel):
    name: str
    bankers_id: UUID
    created_by: UUID


class FinancialAgreementsUpdateDto(BaseModel):
    name: str


class FinancialAgreementsOutDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    bankers_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID
