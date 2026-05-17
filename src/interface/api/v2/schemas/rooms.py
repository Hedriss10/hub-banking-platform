from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints


class RoomCreateSchema(BaseModel):
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)
    ]

    model_config = ConfigDict(str_strip_whitespace=True)


class RoomUpdateSchema(BaseModel):
    name: Optional[
        Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)
        ]
    ] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class RoomOutSchema(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
