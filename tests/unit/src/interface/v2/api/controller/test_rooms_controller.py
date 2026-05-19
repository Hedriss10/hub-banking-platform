from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.interface.api.v2.controller.rooms import (
    RoomsController,
    _room_dto_to_schema,
    _room_employee_dto_to_schema,
    _room_employee_list_dto_to_schema,
)
from src.interface.api.v2.schemas.rooms import (
    RoomCreateSchema,
    RoomEmployeeCreateSchema,
    RoomEmployeeListItemSchema,
    RoomEmployeeOutSchema,
    RoomOutSchema,
    RoomUpdateSchema,
)
from tests.fixtures.room_factories import (
    build_room_dto,
    build_room_employee_dto,
    build_room_employee_list_dto,
)

pytestmark = pytest.mark.unit


def test_room_dto_to_schema_maps_fields() -> None:
    dto = build_room_dto(name='Comando')
    schema = _room_dto_to_schema(dto)
    assert isinstance(schema, RoomOutSchema)
    assert schema.id == dto.id
    assert schema.name == 'Comando'


@pytest.mark.asyncio
async def test_get_all_rooms() -> None:
    items = [build_room_dto(), build_room_dto(name='B')]
    use_case = AsyncMock()
    use_case.get_all_rooms = AsyncMock(return_value=items)
    controller = RoomsController(use_case)
    arrange_result = 2
    out = await controller.get_all_rooms()
    assert len(out) == arrange_result
    assert out[0].name == items[0].name
    use_case.get_all_rooms.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_room_by_id() -> None:
    r = build_room_dto()
    use_case = AsyncMock()
    use_case.get_room_by_id = AsyncMock(return_value=r)
    controller = RoomsController(use_case)

    out = await controller.get_room_by_id(r.id)
    assert out.id == r.id


@pytest.mark.asyncio
async def test_create_room() -> None:
    r = build_room_dto(name='New')
    eid = uuid4()
    use_case = AsyncMock()
    use_case.create_room = AsyncMock(return_value=r)
    controller = RoomsController(use_case)

    body = RoomCreateSchema(name='New')
    out = await controller.create_room(body, eid)

    assert out.name == r.name
    call_dto = use_case.create_room.call_args[0][0]
    assert call_dto.name == 'New'
    assert call_dto.created_by == eid


@pytest.mark.asyncio
async def test_update_room() -> None:
    r = build_room_dto(name='Updated')
    use_case = AsyncMock()
    use_case.update_room = AsyncMock(return_value=r)
    controller = RoomsController(use_case)

    body = RoomUpdateSchema(name='Updated')
    out = await controller.update_room(r.id, body)
    assert out.name == 'Updated'
    use_case.update_room.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room() -> None:
    rid = uuid4()
    use_case = AsyncMock()
    use_case.delete_room = AsyncMock(return_value=None)
    controller = RoomsController(use_case)

    await controller.delete_room(rid)
    use_case.delete_room.assert_awaited_once_with(rid)


def test_room_employee_dto_to_schema_maps_fields() -> None:
    dto = build_room_employee_dto()
    schema = _room_employee_dto_to_schema(dto)
    assert isinstance(schema, RoomEmployeeOutSchema)
    assert schema.id == dto.id
    assert schema.employee_id == dto.employee_id


def test_room_employee_list_dto_to_schema_maps_fields() -> None:
    dto = build_room_employee_list_dto(first_name='Ana', last_name='Costa')
    schema = _room_employee_list_dto_to_schema(dto)
    assert isinstance(schema, RoomEmployeeListItemSchema)
    assert schema.first_name == 'Ana'
    assert schema.last_name == 'Costa'


@pytest.mark.asyncio
async def test_create_room_employee() -> None:
    room = build_room_dto()
    eid = uuid4()
    created = build_room_employee_dto(room_id=room.id, employee_id=eid)
    use_case = AsyncMock()
    use_case.create_room_employee = AsyncMock(return_value=created)
    controller = RoomsController(use_case)

    body = RoomEmployeeCreateSchema(employee_id=eid)
    out = await controller.create_room_employee(room.id, body)

    assert out.employee_id == eid
    call_dto = use_case.create_room_employee.call_args[0][0]
    assert call_dto.room_id == room.id
    assert call_dto.employee_id == eid


@pytest.mark.asyncio
async def test_get_room_employees() -> None:
    room = build_room_dto()
    items = [build_room_employee_list_dto(room_id=room.id)]
    use_case = AsyncMock()
    use_case.get_room_employees = AsyncMock(return_value=items)
    controller = RoomsController(use_case)

    out = await controller.get_room_employees(room.id)

    assert len(out) == 1
    assert out[0].first_name == items[0].first_name
    use_case.get_room_employees.assert_awaited_once_with(room.id)


@pytest.mark.asyncio
async def test_delete_room_employee() -> None:
    rid = uuid4()
    eid = uuid4()
    use_case = AsyncMock()
    use_case.delete_room_employee = AsyncMock(return_value=None)
    controller = RoomsController(use_case)

    await controller.delete_room_employee(rid, eid)

    use_case.delete_room_employee.assert_awaited_once_with(rid, eid)
