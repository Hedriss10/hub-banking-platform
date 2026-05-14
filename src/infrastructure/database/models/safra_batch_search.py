import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class SafraBatchSearchModel(BaseModel):
    __tablename__ = 'safra_batch_search'

    batch_job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    cpf: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    margem: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lotacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    autorizada: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    nome: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    secretaria: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tipoServidor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cargo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    regimeJuridico: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dataAdmissao: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    uf: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    renda: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phone_one: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_two: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_three: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_four: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_five: Mapped[Optional[str]] = mapped_column(String, nullable=True)
