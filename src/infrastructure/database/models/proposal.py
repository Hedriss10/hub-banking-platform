from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee
from src.infrastructure.database.models.common.document import DocumentType
from src.infrastructure.database.models.common.gender import Gender


class ProposalModel(BaseModelWithEmployee):
    __tablename__ = 'proposals'

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    document: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=True)
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    financial_agreements_id: Mapped[UUID] = mapped_column(
        ForeignKey('financial_agreements.id'), nullable=False
    )
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    cpf: Mapped[str] = mapped_column(String(20), nullable=False)
    place_of_birth: Mapped[str] = mapped_column(String(100), nullable=True)
    birth_city: Mapped[str] = mapped_column(String(100), nullable=True)
    birth_state: Mapped[str] = mapped_column(String(100), nullable=True)
    rg_document: Mapped[str] = mapped_column(String(100), nullable=True)
    issuing_authority: Mapped[str] = mapped_column(String(20), nullable=True)
    issuing_state: Mapped[str] = mapped_column(String(2), nullable=True)
    mother_name: Mapped[str] = mapped_column(String(100), nullable=True)
    father_name: Mapped[str] = mapped_column(String(100), nullable=True)
    neighborhood: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    address_number: Mapped[str] = mapped_column(String(20), nullable=True)
    address_complement: Mapped[str] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=True)
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    mobile_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    home_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    work_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    notes: Mapped[str] = mapped_column(String(300), nullable=True)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
