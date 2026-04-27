from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class BankersModel(BaseModelWithEmployee):
    __tablename__ = 'bankers'

    name: Mapped[str] = mapped_column(String(20), nullable=False)
