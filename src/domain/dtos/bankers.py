from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BankerCreateDto(BaseModel):
    name: str
    created_by: UUID


class BankerOutDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime


class BankerUpdateDto(BaseModel):
    name: str
