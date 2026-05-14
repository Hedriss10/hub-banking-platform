from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.validators.cpf_input import CpfSafraStr
from src.interface.api.v2.schemas.enum.safra_bpo_prodcuts import SafraBpoProducts


class TokenOutSchema(BaseModel):
    token: str


class BankerOutSchema(BaseModel):
    codigoBanco: int
    nomeBanco: str
    cnpj: int
    ispb: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class MargemBpoInSchema(BaseModel):
    convenio: int
    cpf: CpfSafraStr
    idProduto: int
    matricula: str

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('idProduto')
    @classmethod
    def validate_id_produto(cls, value: int) -> int:
        SafraBpoProducts(value)
        return value


class MargemBpoOutSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra='ignore',
    )

    cpf: str
    margem: float
    lotacao: str
    autorizada: bool
    nome: str
    secretaria: str
    tipoServidor: str
    cargo: Optional[str] = None
    regimeJuridico: Optional[str] = None
    dataAdmissao: Optional[str] = None
    uf: Optional[str] = None
    renda: Optional[float] = None
    mensagemErro: Optional[str] = None
    dataHoraConsulta: str


class SafraBatchUploadOutSchema(BaseModel):
    """Resposta ao enfileirar processamento do CSV."""

    job_id: UUID
    status: str
    total_rows: int


class SafraBatchJobStatusOutSchema(BaseModel):
    """Status do job em Redis para polling pelo frontend."""

    job_id: UUID
    status: str
    total_rows: int
    processed_rows: int
    failed_rows: int
    detail: Optional[str] = None
