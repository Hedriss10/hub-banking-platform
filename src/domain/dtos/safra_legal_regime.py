from pydantic import BaseModel


class LegalRegimeDTO(BaseModel):
    id: int
    descricao: str
