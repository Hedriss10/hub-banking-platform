from typing import List, Optional
from uuid import UUID

from src.domain.dtos.rooms import RoomCreateDTO, RoomDTO, RoomUpdateDTO
from src.domain.repositories.rooms import RoomRepository


class RoomsService:
    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository

    async def create_room(self, room: RoomCreateDTO) -> RoomDTO:
        return await self.room_repository.create_room(room)

    async def update_room(
        self, room_id: UUID, room: RoomUpdateDTO
    ) -> Optional[RoomDTO]:
        return await self.room_repository.update_room(room_id, room)

    async def delete_room(self, room_id: UUID) -> None:
        return await self.room_repository.delete_room(room_id)

    async def get_room_by_id(self, room_id: UUID) -> Optional[RoomDTO]:
        return await self.room_repository.get_room_by_id(room_id)

    async def get_all_rooms(self) -> List[RoomDTO]:
        return await self.room_repository.get_all_rooms()
