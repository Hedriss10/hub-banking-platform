from datetime import datetime

from pydantic import BaseModel


class SafraTablesOutSchema(BaseModel):
    id: int
    descricao: str
    dtInicioVigencia: datetime
    dtFimVigencia: datetime
