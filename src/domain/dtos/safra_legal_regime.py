from typing import Optional

from pydantic import BaseModel, ConfigDict


class LegalRegimeDTO(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: int
    descricao: Optional[str] = None
