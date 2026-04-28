from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class LoanOperation(BaseModelWithEmployee):
    __tablename__ = 'loan_operation'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
