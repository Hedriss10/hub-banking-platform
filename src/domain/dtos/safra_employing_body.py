from typing import Optional

from pydantic import BaseModel, ConfigDict


class SafraEmployingBodyDTO(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: int
    descricao: Optional[str] = None
