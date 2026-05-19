from pydantic import BaseModel


class SafraEmployingBodyDTO(BaseModel):
    id: int
    descricao: str
