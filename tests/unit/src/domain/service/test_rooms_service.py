from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.rooms import RoomCreateDTO, RoomUpdateDTO
from src.domain.service.rooms import RoomsService
from tests.fixtures.room_factories import build_room_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_room_delegates() -> None:
    dto = RoomCreateDTO(name='Alpha', created_by=uuid4())
    out = build_room_dto(name='Alpha')
    repo = AsyncMock()
    repo.create_room = AsyncMock(return_value=out)
    service = RoomsService(repo)

    result = await service.create_room(dto)

    assert result == out
    repo.create_room.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_get_room_by_id_delegates() -> None:
    rid = uuid4()
    out = build_room_dto()
    repo = AsyncMock()
    repo.get_room_by_id = AsyncMock(return_value=out)
    service = RoomsService(repo)

    assert await service.get_room_by_id(rid) == out
    repo.get_room_by_id.assert_awaited_once_with(rid)


@pytest.mark.asyncio
async def test_get_all_rooms_delegates() -> None:
    items = [build_room_dto()]
    repo = AsyncMock()
    repo.get_all_rooms = AsyncMock(return_value=items)
    service = RoomsService(repo)

    assert await service.get_all_rooms() == items
    repo.get_all_rooms.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_room_delegates() -> None:
    rid = uuid4()
    payload = RoomUpdateDTO(name='Beta')
    out = build_room_dto(name='Beta')
    repo = AsyncMock()
    repo.update_room = AsyncMock(return_value=out)
    service = RoomsService(repo)

    assert await service.update_room(rid, payload) == out
    repo.update_room.assert_awaited_once_with(rid, payload)


@pytest.mark.asyncio
async def test_delete_room_delegates() -> None:
    rid = uuid4()
    repo = AsyncMock()
    repo.delete_room = AsyncMock(return_value=None)
    service = RoomsService(repo)

    await service.delete_room(rid)

    repo.delete_room.assert_awaited_once_with(rid)
