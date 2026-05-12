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
