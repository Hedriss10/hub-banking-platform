from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.rooms import RoomCreateDTO, RoomDTO, RoomUpdateDTO


class RoomRepository(ABC):
    @abstractmethod
    async def get_room_by_id(self, room_id: UUID) -> Optional[RoomDTO]: ...

    @abstractmethod
    async def get_all_rooms(self) -> List[RoomDTO]: ...

    @abstractmethod
    async def create_room(self, room: RoomCreateDTO) -> RoomDTO: ...

    @abstractmethod
    async def update_room(
        self, room_id: UUID, room: RoomUpdateDTO
    ) -> Optional[RoomDTO]: ...

    @abstractmethod
    async def delete_room(self, room_id: UUID) -> None: ...
