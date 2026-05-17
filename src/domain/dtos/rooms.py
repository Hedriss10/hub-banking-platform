from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoomCreateDTO(BaseModel):
    name: str
    created_by: UUID


class RoomUpdateDTO(BaseModel):
    name: Optional[str] = None


class RoomDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
