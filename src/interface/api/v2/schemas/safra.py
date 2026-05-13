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
    cargo: str
    regimeJuridico: str
    dataAdmissao: str
    uf: str
    renda: float
    mensagemErro: str
    dataHoraConsulta: str
