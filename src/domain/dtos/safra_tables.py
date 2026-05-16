from datetime import datetime

from pydantic import BaseModel


class SafraTablesDto(BaseModel):
    id: int
    descricao: str
    dtInicioVigencia: datetime
    dtFimVigencia: datetime
