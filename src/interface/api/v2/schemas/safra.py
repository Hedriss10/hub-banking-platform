from pydantic import BaseModel, ConfigDict


class TokenOutSchema(BaseModel):
    token: str


class BankerOutSchema(BaseModel):
    codigoBanco: int
    nomeBanco: str
    cnpj: int
    ispb: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
