from pydantic import BaseModel


class SafraProfessionsSchema(BaseModel):
    idProfissao: int
    descricao: str
