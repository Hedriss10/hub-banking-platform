from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class FinancialAgreementsModel(BaseModelWithEmployee):
    __tablename__ = 'financial_agreements'

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    bankers_id: Mapped[UUID] = mapped_column(ForeignKey('bankers.id'), nullable=False)
