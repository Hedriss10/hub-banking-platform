from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.core.exceptions.custom import DuplicatedException
from src.domain.dtos.rooms import RoomCreateDTO, RoomUpdateDTO
from src.domain.exceptions.rooms import (
    RoomAlreadyExistsException,
    RoomNotFoundException,
)
from src.domain.use_case.rooms import RoomsUseCase
from tests.fixtures.room_factories import build_room_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_rooms() -> None:
    items = [build_room_dto()]
    service = AsyncMock()
    service.get_all_rooms = AsyncMock(return_value=items)
    uc = RoomsUseCase(service)

    assert await uc.get_all_rooms() == items


@pytest.mark.asyncio
async def test_get_room_success() -> None:
    r = build_room_dto()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=r)
    uc = RoomsUseCase(service)

    assert await uc.get_room_by_id(r.id) == r


@pytest.mark.asyncio
async def test_get_room_not_found() -> None:
    rid = uuid4()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=None)
    uc = RoomsUseCase(service)

    with pytest.raises(RoomNotFoundException, match='not found'):
        await uc.get_room_by_id(rid)


@pytest.mark.asyncio
async def test_create_room_success() -> None:
    dto = RoomCreateDTO(name='Comando', created_by=uuid4())
    created = build_room_dto(name='Comando')
    service = AsyncMock()
    service.create_room = AsyncMock(return_value=created)
    uc = RoomsUseCase(service)

    assert await uc.create_room(dto) == created


@pytest.mark.asyncio
async def test_create_room_duplicate() -> None:
    dto = RoomCreateDTO(name='Comando', created_by=uuid4())
    service = AsyncMock()
    service.create_room = AsyncMock(side_effect=DuplicatedException('dup'))
    uc = RoomsUseCase(service)

    with pytest.raises(RoomAlreadyExistsException):
        await uc.create_room(dto)


@pytest.mark.asyncio
async def test_update_room_success() -> None:
    existing = build_room_dto(name='Old')
    updated = build_room_dto(name='New', id=existing.id)
    data = RoomUpdateDTO(name='New')
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=existing)
    service.update_room = AsyncMock(return_value=updated)
    uc = RoomsUseCase(service)

    assert await uc.update_room(existing.id, data) == updated


@pytest.mark.asyncio
async def test_update_room_not_found_on_get() -> None:
    rid = uuid4()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=None)
    uc = RoomsUseCase(service)

    with pytest.raises(RoomNotFoundException):
        await uc.update_room(rid, RoomUpdateDTO(name='X'))


@pytest.mark.asyncio
async def test_update_room_not_found_after_update() -> None:
    existing = build_room_dto()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=existing)
    service.update_room = AsyncMock(return_value=None)
    uc = RoomsUseCase(service)

    with pytest.raises(RoomNotFoundException):
        await uc.update_room(existing.id, RoomUpdateDTO(name='X'))


@pytest.mark.asyncio
async def test_update_room_duplicate() -> None:
    existing = build_room_dto()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=existing)
    service.update_room = AsyncMock(side_effect=DuplicatedException('dup'))
    uc = RoomsUseCase(service)

    with pytest.raises(RoomAlreadyExistsException):
        await uc.update_room(existing.id, RoomUpdateDTO(name='Taken'))


@pytest.mark.asyncio
async def test_delete_room_success() -> None:
    existing = build_room_dto()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=existing)
    service.delete_room = AsyncMock(return_value=None)
    uc = RoomsUseCase(service)

    await uc.delete_room(existing.id)

    service.delete_room.assert_awaited_once_with(existing.id)


@pytest.mark.asyncio
async def test_delete_room_not_found() -> None:
    rid = uuid4()
    service = AsyncMock()
    service.get_room_by_id = AsyncMock(return_value=None)
    uc = RoomsUseCase(service)

    with pytest.raises(RoomNotFoundException):
        await uc.delete_room(rid)
