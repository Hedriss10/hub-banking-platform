from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.enum.proposal_loan import ProposalLoanStatus


class CreatedProposalLoanDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    server_password: Optional[str] = None
    registration_number: Optional[str] = None
    dispatch_date: Optional[datetime] = None
    available_margin: Optional[float] = None
    status: Optional[ProposalLoanStatus] = None
    term_start: Optional[int] = None
    term_end: Optional[int] = None
    operation_amount: Optional[Decimal] = None
    proposal_id: Optional[UUID] = None
    finance_table_id: Optional[int] = None
    financial_agreement_id: Optional[UUID] = None
    loan_operation_id: Optional[int] = None
    created_by: UUID


class ProposalLoanOutDTO(CreatedProposalLoanDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
