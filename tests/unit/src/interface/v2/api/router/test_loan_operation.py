from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from tests.fixtures.loan_operation_factories import build_loan_operation_out_dto

pytestmark = pytest.mark.unit

_LOAN_OPERATIONS = '/api/v2/loan-operations'


@pytest.mark.asyncio
async def test_post_create_loan_operation(
    async_loan_operation_client: AsyncClient,
    mock_loan_operation_use_case: AsyncMock,
) -> None:
    created = build_loan_operation_out_dto(name='Loan Alpha')
    mock_loan_operation_use_case.create_loan_operation = AsyncMock(
        return_value=created,
    )

    response = await async_loan_operation_client.post(
        _LOAN_OPERATIONS,
        json={'name': 'Loan Alpha'},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == 'Loan Alpha'
    mock_loan_operation_use_case.create_loan_operation.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_loan_operations(
    async_loan_operation_client: AsyncClient,
    mock_loan_operation_use_case: AsyncMock,
) -> None:
    lo = build_loan_operation_out_dto()
    mock_loan_operation_use_case.list_loan_operations = AsyncMock(
        return_value=[lo],
    )

    response = await async_loan_operation_client.get(_LOAN_OPERATIONS)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(lo.id)


@pytest.mark.asyncio
async def test_get_loan_operation_by_id(
    async_loan_operation_client: AsyncClient,
    mock_loan_operation_use_case: AsyncMock,
) -> None:
    lo = build_loan_operation_out_dto()
    mock_loan_operation_use_case.get_loan_operation = AsyncMock(return_value=lo)

    response = await async_loan_operation_client.get(
        f'{_LOAN_OPERATIONS}/{lo.id}',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(lo.id)


@pytest.mark.asyncio
async def test_patch_update_loan_operation(
    async_loan_operation_client: AsyncClient,
    mock_loan_operation_use_case: AsyncMock,
) -> None:
    lo = build_loan_operation_out_dto()
    updated = build_loan_operation_out_dto(name='Updated loan', id=lo.id)
    mock_loan_operation_use_case.update_loan_operation = AsyncMock(
        return_value=updated,
    )

    response = await async_loan_operation_client.patch(
        f'{_LOAN_OPERATIONS}/{lo.id}',
        json={'name': 'Updated loan'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == 'Updated loan'
    mock_loan_operation_use_case.update_loan_operation.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_loan_operation(
    async_loan_operation_client: AsyncClient,
    mock_loan_operation_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    mock_loan_operation_use_case.delete_loan_operation = AsyncMock(
        return_value=None,
    )

    response = await async_loan_operation_client.delete(
        f'{_LOAN_OPERATIONS}/{eid}',
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_loan_operation_use_case.delete_loan_operation.assert_awaited_once_with(
        eid,
    )
