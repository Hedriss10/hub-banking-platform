from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from tests.fixtures.room_factories import (
    build_room_dto,
    build_room_employee_dto,
    build_room_employee_list_dto,
)

pytestmark = pytest.mark.unit

_ROOMS = '/api/v2/rooms'


@pytest.mark.asyncio
async def test_post_create_room(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    created = build_room_dto(name='Comando')
    mock_rooms_use_case.create_room = AsyncMock(return_value=created)

    response = await async_rooms_client.post(_ROOMS, json={'name': 'Comando'})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == 'Comando'
    mock_rooms_use_case.create_room.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_rooms(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    r = build_room_dto()
    mock_rooms_use_case.get_all_rooms = AsyncMock(return_value=[r])

    response = await async_rooms_client.get(_ROOMS)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(r.id)


@pytest.mark.asyncio
async def test_get_room_by_id(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    r = build_room_dto()
    mock_rooms_use_case.get_room_by_id = AsyncMock(return_value=r)

    response = await async_rooms_client.get(f'{_ROOMS}/{r.id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(r.id)


@pytest.mark.asyncio
async def test_patch_update_room(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    r = build_room_dto()
    updated = build_room_dto(name='Novo', id=r.id)
    mock_rooms_use_case.update_room = AsyncMock(return_value=updated)

    response = await async_rooms_client.patch(
        f'{_ROOMS}/{r.id}',
        json={'name': 'Novo'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == 'Novo'
    mock_rooms_use_case.update_room.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    rid = uuid4()
    mock_rooms_use_case.delete_room = AsyncMock(return_value=None)

    response = await async_rooms_client.delete(f'{_ROOMS}/{rid}')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_rooms_use_case.delete_room.assert_awaited_once_with(rid)


@pytest.mark.asyncio
async def test_get_list_room_employees(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    room = build_room_dto()
    employee = build_room_employee_list_dto(room_id=room.id)
    mock_rooms_use_case.get_room_employees = AsyncMock(return_value=[employee])

    response = await async_rooms_client.get(f'{_ROOMS}/{room.id}/employees')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['first_name'] == employee.first_name
    assert data[0]['last_name'] == employee.last_name
    mock_rooms_use_case.get_room_employees.assert_awaited_once_with(room.id)


@pytest.mark.asyncio
async def test_post_create_room_employee(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    room = build_room_dto()
    eid = uuid4()
    created = build_room_employee_dto(room_id=room.id, employee_id=eid)
    mock_rooms_use_case.create_room_employee = AsyncMock(return_value=created)

    response = await async_rooms_client.post(
        f'{_ROOMS}/{room.id}/employees',
        json={'employee_id': str(eid)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['employee_id'] == str(eid)
    mock_rooms_use_case.create_room_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_room_employee(
    async_rooms_client: AsyncClient,
    mock_rooms_use_case: AsyncMock,
) -> None:
    room = build_room_dto()
    eid = uuid4()
    mock_rooms_use_case.delete_room_employee = AsyncMock(return_value=None)

    response = await async_rooms_client.delete(
        f'{_ROOMS}/{room.id}/employees/{eid}',
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_rooms_use_case.delete_room_employee.assert_awaited_once_with(room.id, eid)
