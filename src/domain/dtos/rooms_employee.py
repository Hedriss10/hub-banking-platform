from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoomEmployeeCreateDTO(BaseModel):
    room_id: UUID
    employee_id: UUID


class RoomEmployeeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID
    employee_id: UUID


class RoomEmployeeListDTO(BaseModel):
    id: UUID
    room_id: UUID
    employee_id: UUID
    first_name: str
    last_name: str
