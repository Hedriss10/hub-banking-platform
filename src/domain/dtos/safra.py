from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.validators.cpf_input import CpfSafraStr

_ID_PRODUTO_VALID = frozenset({1, 2, 5, 7})


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    token: str


class BankerResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    codigoBanco: int
    nomeBanco: str
    cnpj: int
    ispb: int


class MargemBpoDto(BaseModel):
    """
    Dto para consultar margem de acordo com a consulta da api da Safra
    """

    convenio: int
    cpf: CpfSafraStr
    idProduto: int
    matricula: str

    model_config = ConfigDict(extra='ignore')

    @field_validator('idProduto')
    @classmethod
    def validate_id_produto(cls, value: int) -> int:
        if value not in _ID_PRODUTO_VALID:
            raise ValueError('idProduto deve ser 1, 2, 5 ou 7')
        return value


class SafraBatchSearchDto(BaseModel):
    """
    Linha do CSV / payload de batch Safra (consulta margem em lote).
    """

    convenio: int
    idProduto: int
    cpf: CpfSafraStr
    matricula: str

    phone_one: Optional[str] = None
    phone_two: Optional[str] = None
    phone_three: Optional[str] = None
    phone_four: Optional[str] = None
    phone_five: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

    @field_validator('idProduto')
    @classmethod
    def validate_id_produto(cls, value: int) -> int:
        if value not in _ID_PRODUTO_VALID:
            raise ValueError('idProduto deve ser 1, 2, 5 ou 7')
        return value

    @field_validator(
        'phone_one',
        'phone_two',
        'phone_three',
        'phone_four',
        'phone_five',
        mode='before',
    )
    @classmethod
    def strip_optional_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped or None


class MargemBpoOutputDto(BaseModel):
    """Resposta da consulta de margem BPO (API Safra).

    A Safra pode omitir ou enviar null em vários campos conforme o servidor.
    """

    model_config = ConfigDict(extra='ignore')

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
