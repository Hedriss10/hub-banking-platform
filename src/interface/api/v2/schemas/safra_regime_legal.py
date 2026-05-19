from pydantic import BaseModel


class SafraRegimeLegalSchema(BaseModel):
    id: int
    descricao: str
