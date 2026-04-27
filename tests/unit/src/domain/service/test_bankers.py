from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.bankers import BankerCreateDto, BankerUpdateDto
from src.domain.service.bankers import BankersService
from tests.fixtures.banker_factories import build_banker_out_dto

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_bankers_delegates_to_repository() -> None:
    out = [build_banker_out_dto()]
    repo = AsyncMock()
    repo.list_bankers = AsyncMock(return_value=out)
    service = BankersService(repo)

    result = await service.list_bankers()

    assert result == out
    repo.list_bankers.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_banker_delegates_to_repository() -> None:
    eid = uuid4()
    out = build_banker_out_dto()
    repo = AsyncMock()
    repo.get_banker = AsyncMock(return_value=out)
    service = BankersService(repo)

    result = await service.get_banker(eid)

    assert result == out
    repo.get_banker.assert_awaited_once_with(eid)


@pytest.mark.asyncio
async def test_create_banker_delegates_to_repository() -> None:
    dto = BankerCreateDto(name='Banco A', created_by=uuid4())
    out = build_banker_out_dto()
    repo = AsyncMock()
    repo.create_banker = AsyncMock(return_value=out)
    service = BankersService(repo)

    result = await service.create_banker(dto)

    assert result == out
    repo.create_banker.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_update_banker_delegates_to_repository() -> None:
    eid = uuid4()
    dto = BankerUpdateDto(name='Novo Nome')
    out = build_banker_out_dto()
    repo = AsyncMock()
    repo.update_banker = AsyncMock(return_value=out)
    service = BankersService(repo)

    result = await service.update_banker(eid, dto)

    assert result == out
    repo.update_banker.assert_awaited_once_with(eid, dto)


@pytest.mark.asyncio
async def test_delete_banker_delegates_to_repository() -> None:
    eid = uuid4()
    repo = AsyncMock()
    repo.delete_banker = AsyncMock(return_value=None)
    service = BankersService(repo)

    await service.delete_banker(eid)

    repo.delete_banker.assert_awaited_once_with(eid)
