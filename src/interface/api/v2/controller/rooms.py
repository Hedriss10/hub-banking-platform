from typing import List
from uuid import UUID

from src.domain.dtos.rooms import RoomCreateDTO, RoomDTO, RoomUpdateDTO
from src.domain.use_case.rooms import RoomsUseCase
from src.interface.api.v2.schemas.rooms import (
    RoomCreateSchema,
    RoomOutSchema,
    RoomUpdateSchema,
)


def _room_dto_to_schema(dto: RoomDTO) -> RoomOutSchema:
    return RoomOutSchema.model_validate(dto.model_dump())


class RoomsController:
    def __init__(self, rooms_use_case: RoomsUseCase):
        self.rooms_use_case = rooms_use_case

    async def create_room(
        self,
        room: RoomCreateSchema,
        created_by: UUID,
    ) -> RoomOutSchema:
        dto = RoomCreateDTO(name=room.name, created_by=created_by)
        created = await self.rooms_use_case.create_room(dto)
        return _room_dto_to_schema(created)

    async def update_room(
        self,
        room_id: UUID,
        room: RoomUpdateSchema,
    ) -> RoomOutSchema:
        dto = RoomUpdateDTO.model_validate(
            room.model_dump(exclude_unset=True, exclude_none=True),
        )
        updated = await self.rooms_use_case.update_room(room_id, dto)
        return _room_dto_to_schema(updated)

    async def delete_room(self, room_id: UUID) -> None:
        await self.rooms_use_case.delete_room(room_id)

    async def get_room_by_id(self, room_id: UUID) -> RoomOutSchema:
        found = await self.rooms_use_case.get_room_by_id(room_id)
        return _room_dto_to_schema(found)

    async def get_all_rooms(self) -> List[RoomOutSchema]:
        rooms = await self.rooms_use_case.get_all_rooms()
        return [_room_dto_to_schema(row) for row in rooms]
