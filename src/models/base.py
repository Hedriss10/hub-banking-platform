import re
from datetime import datetime

from sqlalchemy import Integer, DateTime, text, Boolean
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import MetaData

from src.core.settings import settings



@as_declarative()
class BaseModel:
    metadata = MetaData(schema=settings.POSTGRES_SCHEMA)
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=text("timezone('utc', now())"),
        nullable=False,
    )

    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Converte o nome da classe em snake_case.
        Ex:  UserAccount -> user_account
        """
        cls_name = cls.__name__  # type: ignore[attr-defined]
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', cls_name).lower()
        return snake



