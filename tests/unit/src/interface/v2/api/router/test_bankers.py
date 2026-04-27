from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from tests.fixtures.banker_factories import build_banker_out_dto

pytestmark = pytest.mark.unit

_BANKERS = '/api/v2/bankers'


@pytest.mark.asyncio
async def test_post_create_banker(
    async_bankers_client: AsyncClient,
    mock_bankers_use_case: AsyncMock,
) -> None:
    created = build_banker_out_dto(name='Banco Criar')
    mock_bankers_use_case.create_banker = AsyncMock(return_value=created)

    response = await async_bankers_client.post(
        _BANKERS,
        json={'name': 'Banco Criar'},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == 'Banco Criar'
    mock_bankers_use_case.create_banker.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_bankers(
    async_bankers_client: AsyncClient,
    mock_bankers_use_case: AsyncMock,
) -> None:
    b = build_banker_out_dto()
    mock_bankers_use_case.list_bankers = AsyncMock(return_value=[b])

    response = await async_bankers_client.get(_BANKERS)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(b.id)


@pytest.mark.asyncio
async def test_get_banker_by_id(
    async_bankers_client: AsyncClient,
    mock_bankers_use_case: AsyncMock,
) -> None:
    b = build_banker_out_dto()
    mock_bankers_use_case.get_banker = AsyncMock(return_value=b)

    response = await async_bankers_client.get(f'{_BANKERS}/{b.id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(b.id)


@pytest.mark.asyncio
async def test_patch_update_banker(
    async_bankers_client: AsyncClient,
    mock_bankers_use_case: AsyncMock,
) -> None:
    b = build_banker_out_dto()
    updated = build_banker_out_dto(name='Novo Banco Aqui', id=b.id)
    mock_bankers_use_case.update_banker = AsyncMock(return_value=updated)

    response = await async_bankers_client.patch(
        f'{_BANKERS}/{b.id}',
        json={'name': 'Novo Banco Aqui'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == 'Novo Banco Aqui'
    mock_bankers_use_case.update_banker.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_banker(
    async_bankers_client: AsyncClient,
    mock_bankers_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    mock_bankers_use_case.delete_banker = AsyncMock(return_value=None)

    response = await async_bankers_client.delete(f'{_BANKERS}/{eid}')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_bankers_use_case.delete_banker.assert_awaited_once_with(eid)
