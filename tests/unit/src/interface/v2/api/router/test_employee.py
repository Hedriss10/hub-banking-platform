from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from tests.fixtures.employee_factories import build_employee_dto

pytestmark = pytest.mark.unit

_EMPLOYEES = '/api/v2/employees'


@pytest.mark.asyncio
async def test_post_create_employee(
    async_employee_client: AsyncClient,
    mock_employee_use_case: AsyncMock,
    employee_create_dto,
) -> None:
    created = build_employee_dto(email=employee_create_dto.email)
    mock_employee_use_case.create_employee = AsyncMock(return_value=created)

    payload = employee_create_dto.model_dump(mode='json')
    response = await async_employee_client.post(_EMPLOYEES, json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body['email'] == created.email
    mock_employee_use_case.create_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_employees(
    async_employee_client: AsyncClient,
    mock_employee_use_case: AsyncMock,
    employee_dto,
) -> None:
    mock_employee_use_case.list_employee = AsyncMock(return_value=[employee_dto])

    response = await async_employee_client.get(_EMPLOYEES)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(employee_dto.id)


@pytest.mark.asyncio
async def test_get_employee_by_id(
    async_employee_client: AsyncClient,
    mock_employee_use_case: AsyncMock,
    employee_dto,
) -> None:
    mock_employee_use_case.get_employee = AsyncMock(return_value=employee_dto)
    eid = employee_dto.id

    response = await async_employee_client.get(f'{_EMPLOYEES}/{eid}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(eid)


@pytest.mark.asyncio
async def test_patch_update_employee(
    async_employee_client: AsyncClient,
    mock_employee_use_case: AsyncMock,
    employee_dto,
) -> None:
    updated = build_employee_dto(first_name='Novo')
    mock_employee_use_case.update_employee = AsyncMock(return_value=updated)
    eid = employee_dto.id

    response = await async_employee_client.patch(
        f'{_EMPLOYEES}/{eid}',
        json={'first_name': 'Novo'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['first_name'] == 'Novo'
    mock_employee_use_case.update_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_employee(
    async_employee_client: AsyncClient,
    mock_employee_use_case: AsyncMock,
) -> None:
    mock_employee_use_case.delete_employee = AsyncMock(return_value=None)
    eid = uuid4()

    response = await async_employee_client.delete(f'{_EMPLOYEES}/{eid}')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_employee_use_case.delete_employee.assert_awaited_once_with(eid)
