from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class RoomsModel(BaseModelWithEmployee):
    __tablename__ = 'rooms'
    __table_args__ = (
        Index(
            'uq_rooms_name_not_deleted',
            'name',
            unique=True,
            postgresql_where=text('is_deleted = false'),
        ),
    )

    name: Mapped[str] = mapped_column(String(30), nullable=False)
