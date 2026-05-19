from typing import List
from uuid import UUID

from src.core.exceptions.custom import DuplicatedException
from src.domain.dtos.rooms import RoomCreateDTO, RoomDTO, RoomUpdateDTO
from src.domain.dtos.rooms_employee import (
    RoomEmployeeCreateDTO,
    RoomEmployeeDTO,
    RoomEmployeeListDTO,
)
from src.domain.exceptions.rooms import (
    RoomAlreadyExistsException,
    RoomNotFoundException,
)
from src.domain.service.rooms import RoomsService


class RoomsUseCase:
    def __init__(self, room_service: RoomsService):
        self.room_service = room_service

    async def create_room(self, room: RoomCreateDTO) -> RoomDTO:
        try:
            return await self.room_service.create_room(room)
        except DuplicatedException as error:
            raise RoomAlreadyExistsException() from error

    async def update_room(self, room_id: UUID, room: RoomUpdateDTO) -> RoomDTO:
        existing = await self.room_service.get_room_by_id(room_id)
        if not existing:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        try:
            updated = await self.room_service.update_room(room_id, room)
        except DuplicatedException as error:
            raise RoomAlreadyExistsException() from error
        if not updated:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        return updated

    async def delete_room(self, room_id: UUID) -> None:
        existing = await self.room_service.get_room_by_id(room_id)
        if not existing:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        await self.room_service.delete_room(room_id)

    async def get_room_by_id(self, room_id: UUID) -> RoomDTO:
        room = await self.room_service.get_room_by_id(room_id)
        if not room:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        return room

    async def get_all_rooms(self) -> List[RoomDTO]:
        return await self.room_service.get_all_rooms()

    async def create_room_employee(
        self, room_employee: RoomEmployeeCreateDTO
    ) -> RoomEmployeeDTO:
        existing = await self.room_service.get_room_by_id(room_employee.room_id)
        if not existing:
            raise RoomNotFoundException(
                message=f'Room with id {room_employee.room_id} not found',
            )
        return await self.room_service.create_room_employee(room_employee)

    async def get_room_employees(self, room_id: UUID) -> List[RoomEmployeeListDTO]:
        existing = await self.room_service.get_room_by_id(room_id)
        if not existing:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        return await self.room_service.get_room_employees(room_id)

    async def delete_room_employee(self, room_id: UUID, employee_id: UUID) -> None:
        existing = await self.room_service.get_room_by_id(room_id)
        if not existing:
            raise RoomNotFoundException(
                message=f'Room with id {room_id} not found',
            )
        await self.room_service.delete_room_employee(room_id, employee_id)
