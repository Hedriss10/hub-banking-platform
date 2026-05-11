from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreatedProposalAccountDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bank_agency: Optional[str] = None
    pix_key: Optional[str] = None
    account_number: Optional[str] = None
    agency_digit: Optional[str] = None
    agency_operation: Optional[str] = None
    agency_operation_digit: Optional[str] = None
    account_type: Optional[str] = None
    payment_type: Optional[str] = None
    bank_id: Optional[UUID] = None
    proposal_id: Optional[UUID] = None
    created_by: UUID


class ProposalAccountOutDTO(CreatedProposalAccountDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
