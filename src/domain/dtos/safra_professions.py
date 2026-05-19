from pydantic import BaseModel


class SafraProfessionsDTO(BaseModel):
    idProfissao: int
    descricao: str
