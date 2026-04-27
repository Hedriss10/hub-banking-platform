from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee
from src.infrastructure.database.models.common.proposal_loan import ProposalLoanStatus


class ProposalLoanModel(BaseModelWithEmployee):
    server_password: Mapped[str] = mapped_column(String(40), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(40), nullable=True)
    dispatch_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    available_margin: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[ProposalLoanStatus] = mapped_column(
        Enum(ProposalLoanStatus), default='WAITING_TYPING', nullable=True
    )
    term_start: Mapped[int] = mapped_column(Integer, nullable=True)
    term_end: Mapped[int] = mapped_column(Integer, nullable=True)
    operation_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0.0, nullable=True
    )
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey('proposals.id'), nullable=True)
    finance_table_id: Mapped[UUID] = mapped_column(Integer, nullable=True)
    financial_agreement_id: Mapped[UUID] = mapped_column(
        ForeignKey('financial_agreements.id'), nullable=True
    )
    loan_operation_id: Mapped[UUID] = mapped_column(Integer, nullable=True)
