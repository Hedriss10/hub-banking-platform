from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class RoomsModel(BaseModelWithEmployee):
    __tablename__ = 'rooms'

    name: Mapped[str] = mapped_column(String(30), nullable=False)
