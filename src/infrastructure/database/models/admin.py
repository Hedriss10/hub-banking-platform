from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum
from src.infrastructure.database.models.base import BaseModel
from src.infrastructure.database.models.common.role import RoleStatus


class Admin(BaseModel):
    __tablename__ = 'admins'

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleStatus] = mapped_column(Enum(RoleStatus), nullable=False)
