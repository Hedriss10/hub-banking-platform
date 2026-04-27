from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.bankers import BankerCreateDto, BankerUpdateDto
from src.domain.exceptions.bankers import BankerNotFoundException
from src.domain.use_case.bankers import BankersUseCase
from tests.fixtures.banker_factories import build_banker_out_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_bankers() -> None:
    items = [build_banker_out_dto()]
    service = AsyncMock()
    service.list_bankers = AsyncMock(return_value=items)
    uc = BankersUseCase(service)

    result = await uc.list_bankers()

    assert result == items


@pytest.mark.asyncio
async def test_get_banker_success() -> None:
    b = build_banker_out_dto()
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=b)
    uc = BankersUseCase(service)

    out = await uc.get_banker(b.id)

    assert out == b


@pytest.mark.asyncio
async def test_get_banker_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=None)
    uc = BankersUseCase(service)

    with pytest.raises(BankerNotFoundException, match='not found'):
        await uc.get_banker(eid)


@pytest.mark.asyncio
async def test_create_banker() -> None:
    dto = BankerCreateDto(name='Banco', created_by=uuid4())
    created = build_banker_out_dto()
    service = AsyncMock()
    service.create_banker = AsyncMock(return_value=created)
    uc = BankersUseCase(service)

    out = await uc.create_banker(dto)

    assert out == created


@pytest.mark.asyncio
async def test_update_banker_success() -> None:
    b = build_banker_out_dto()
    updated = build_banker_out_dto(name='Atual')
    data = BankerUpdateDto(name='Atual')
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=b)
    service.update_banker = AsyncMock(return_value=updated)
    uc = BankersUseCase(service)

    out = await uc.update_banker(b.id, data)

    assert out == updated


@pytest.mark.asyncio
async def test_update_banker_not_found_on_get() -> None:
    eid = uuid4()
    data = BankerUpdateDto(name='X')
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=None)
    uc = BankersUseCase(service)

    with pytest.raises(BankerNotFoundException):
        await uc.update_banker(eid, data)


@pytest.mark.asyncio
async def test_update_banker_not_found_after_update() -> None:
    b = build_banker_out_dto()
    data = BankerUpdateDto(name='X')
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=b)
    service.update_banker = AsyncMock(return_value=None)
    uc = BankersUseCase(service)

    with pytest.raises(BankerNotFoundException):
        await uc.update_banker(b.id, data)


@pytest.mark.asyncio
async def test_delete_banker() -> None:
    b = build_banker_out_dto()
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=b)
    service.delete_banker = AsyncMock(return_value=None)
    uc = BankersUseCase(service)

    await uc.delete_banker(b.id)

    service.delete_banker.assert_awaited_once_with(b.id)


@pytest.mark.asyncio
async def test_delete_banker_not_found() -> None:
    eid = uuid4()
    service = AsyncMock()
    service.get_banker = AsyncMock(return_value=None)
    uc = BankersUseCase(service)

    with pytest.raises(BankerNotFoundException):
        await uc.delete_banker(eid)
