from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FinancialAgreementsCreateSchema(BaseModel):
    name: str
    bank_id: UUID


class FinancialAgreementsUpdateSchema(BaseModel):
    name: str


class FinancialAgreementsOutSchema(BaseModel):
    id: UUID
    name: str
    bank_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID
