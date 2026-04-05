import re
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, as_declarative, declared_attr, mapped_column
from sqlalchemy.schema import MetaData

from src.core.config.settings import get_settings

settings = get_settings()


@as_declarative()
class BaseModel:
    metadata = MetaData(schema=settings.POSTGRES_SCHEMA)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("timezone('utc', now())"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
        nullable=False,
    )

    is_deleted: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Converte o nome da classe em snake_case.
        Ex:  UserAccount -> user_account
        """
        cls_name = cls.__name__  # type: ignore[attr-defined]
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', cls_name).lower()
        return snake


class BaseModelWithEmployee(BaseModel):
    __abstract__ = True

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('employees.id'), nullable=False, index=True
    )
