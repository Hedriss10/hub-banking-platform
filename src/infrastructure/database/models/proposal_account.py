from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class ProposalPaymentAccountModel(BaseModelWithEmployee):
    __tablename__ = 'proposal_acounts'

    bank_agency: Mapped[str] = mapped_column(String(100), nullable=True)
    pix_key: Mapped[str] = mapped_column(String(120), nullable=True)
    account_number: Mapped[str] = mapped_column(String(20), nullable=True)
    agency_digit: Mapped[str] = mapped_column(String(10), nullable=True)
    agency_operation: Mapped[str] = mapped_column(String(10), nullable=True)
    agency_operation_digit: Mapped[str] = mapped_column(String(10), nullable=True)
    account_type: Mapped[str] = mapped_column(String(50), nullable=True)
    payment_type: Mapped[str] = mapped_column(String, nullable=True)
    bank_id: Mapped[UUID] = mapped_column(ForeignKey('bankers.id'), nullable=True)
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey('proposals.id'), nullable=True)
