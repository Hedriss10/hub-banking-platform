from typing import Optional

from pydantic import BaseModel, ConfigDict


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
    cpf: int
    idProduto: int
    matricula: str

    model_config = ConfigDict(str_strip_whitespace=True)


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
