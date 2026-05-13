from pydantic import BaseModel, ConfigDict


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
    cpf: int
    idProduto: int
    matricula: str

    model_config = ConfigDict(extra='ignore')


class MargemBpoOutputDto(BaseModel):
    """Resposta da consulta de margem BPO (API Safra)."""

    model_config = ConfigDict(extra='ignore')

    cpf: str
    margem: float
    lotacao: str
    autorizada: bool
    nome: str
    secretaria: str
    tipoServidor: str
    cargo: str
    regimeJuridico: str
    dataAdmissao: str
    uf: str
    renda: float
    mensagemErro: str
    dataHoraConsulta: str
