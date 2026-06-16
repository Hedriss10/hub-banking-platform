from typing import Optional

from pydantic import BaseModel, ConfigDict


class SafraProfessionsDTO(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProfissao: int
    descricao: Optional[str] = None
