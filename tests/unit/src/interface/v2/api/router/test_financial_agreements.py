from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from tests.fixtures.financial_agreements_factories import (
    build_financial_agreement_out_dto,
)

pytestmark = pytest.mark.unit

_FINANCIAL_AGREEMENTS = '/api/v2/financial-agreements'


@pytest.mark.asyncio
async def test_post_create_financial_agreement(
    async_financial_agreements_client: AsyncClient,
    mock_financial_agreements_use_case: AsyncMock,
) -> None:
    bid = uuid4()
    created = build_financial_agreement_out_dto(name='Agreement Alpha', bankers_id=bid)
    mock_financial_agreements_use_case.create_financial_agreement = AsyncMock(
        return_value=created,
    )

    response = await async_financial_agreements_client.post(
        _FINANCIAL_AGREEMENTS,
        json={'name': 'Agreement Alpha', 'bank_id': str(bid)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == 'Agreement Alpha'
    mock_financial_agreements_use_case.create_financial_agreement.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_financial_agreements_by_bank(
    async_financial_agreements_client: AsyncClient,
    mock_financial_agreements_use_case: AsyncMock,
) -> None:
    bid = uuid4()
    fa = build_financial_agreement_out_dto(bankers_id=bid)
    mock_financial_agreements_use_case.list_financial_agreements = AsyncMock(
        return_value=[fa],
    )

    response = await async_financial_agreements_client.get(
        f'{_FINANCIAL_AGREEMENTS}/banks/{bid}',
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(fa.id)
    assert data[0]['bank_id'] == str(bid)


@pytest.mark.asyncio
async def test_get_financial_agreement_by_id(
    async_financial_agreements_client: AsyncClient,
    mock_financial_agreements_use_case: AsyncMock,
) -> None:
    fa = build_financial_agreement_out_dto()
    mock_financial_agreements_use_case.get_financial_agreement = AsyncMock(
        return_value=fa,
    )

    response = await async_financial_agreements_client.get(
        f'{_FINANCIAL_AGREEMENTS}/{fa.id}',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(fa.id)


@pytest.mark.asyncio
async def test_patch_update_financial_agreement(
    async_financial_agreements_client: AsyncClient,
    mock_financial_agreements_use_case: AsyncMock,
) -> None:
    fa = build_financial_agreement_out_dto()
    updated = build_financial_agreement_out_dto(name='Updated agreement', id=fa.id)
    mock_financial_agreements_use_case.update_financial_agreement = AsyncMock(
        return_value=updated,
    )

    response = await async_financial_agreements_client.patch(
        f'{_FINANCIAL_AGREEMENTS}/{fa.id}',
        json={'name': 'Updated agreement'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == 'Updated agreement'
    mock_financial_agreements_use_case.update_financial_agreement.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_financial_agreement(
    async_financial_agreements_client: AsyncClient,
    mock_financial_agreements_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    mock_financial_agreements_use_case.delete_financial_agreement = AsyncMock(
        return_value=None,
    )

    response = await async_financial_agreements_client.delete(
        f'{_FINANCIAL_AGREEMENTS}/{eid}',
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_financial_agreements_use_case.delete_financial_agreement.assert_awaited_once_with(
        eid,
    )
