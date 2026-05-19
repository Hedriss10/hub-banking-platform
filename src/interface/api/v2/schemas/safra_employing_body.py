from pydantic import BaseModel


class SafraEmployingBodySchema(BaseModel):
    id: int
    descricao: str
