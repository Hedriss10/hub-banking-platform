from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SafraTablesDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: Optional[int] = None
    descricao: Optional[str] = None
    dtInicioVigencia: Optional[datetime] = None
    dtFimVigencia: Optional[datetime] = None
