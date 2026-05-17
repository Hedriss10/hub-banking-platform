from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class RoomsEmployee(BaseModel):
    __tablename__ = 'rooms_employees'

    room_id: Mapped[UUID] = mapped_column(ForeignKey('rooms.id'), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey('employees.id'), nullable=False
    )
