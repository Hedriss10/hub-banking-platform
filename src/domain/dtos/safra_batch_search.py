from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SafraBatchSearchExportRowDTO(BaseModel):
    """Linha de `safra_batch_search` para leitura e export CSV."""

    model_config = ConfigDict(from_attributes=True)

    batch_job_id: UUID
    cpf: Optional[str] = None
    margem: Optional[float] = None
    lotacao: Optional[str] = None
    autorizada: Optional[bool] = None
    nome: Optional[str] = None
    secretaria: Optional[str] = None
    tipoServidor: Optional[str] = None
    cargo: Optional[str] = None
    regimeJuridico: Optional[str] = None
    dataAdmissao: Optional[datetime] = None
    uf: Optional[str] = None
    renda: Optional[float] = None
    phone_one: Optional[str] = None
    phone_two: Optional[str] = None
    phone_three: Optional[str] = None
    phone_four: Optional[str] = None
    phone_five: Optional[str] = None
