from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class BankerCreateSchema(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=20)]

    model_config = ConfigDict(str_strip_whitespace=True)


class BankerOutSchema(BaseModel):
    id: str
    name: str
    created_at: datetime


class BankerUpdateSchema(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=20)]

    model_config = ConfigDict(str_strip_whitespace=True)
