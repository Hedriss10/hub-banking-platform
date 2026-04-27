from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.interface.api.v2.controller.bankers import (
    BankersController,
    _banker_out_to_schema,
)
from src.interface.api.v2.schemas.bankers import (
    BankerCreateSchema,
    BankerOutSchema,
    BankerUpdateSchema,
)
from tests.fixtures.banker_factories import build_banker_out_dto

pytestmark = pytest.mark.unit


RESULT_LIST_BANKERS = 2


def test_banker_out_to_schema_maps_fields() -> None:
    dto = build_banker_out_dto(name='Minha Caixa')
    schema = _banker_out_to_schema(dto)
    assert isinstance(schema, BankerOutSchema)
    assert schema.id == str(dto.id)
    assert schema.name == 'Minha Caixa'


@pytest.mark.asyncio
async def test_list_bankers() -> None:
    items = [build_banker_out_dto(), build_banker_out_dto(name='B2')]
    use_case = AsyncMock()
    use_case.list_bankers = AsyncMock(return_value=items)
    controller = BankersController(use_case)

    out = await controller.list_bankers()
    assert len(out) == RESULT_LIST_BANKERS
    assert out[0].id == str(items[0].id)
    assert out[1].name == 'B2'
    use_case.list_bankers.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_banker() -> None:
    b = build_banker_out_dto()
    use_case = AsyncMock()
    use_case.get_banker = AsyncMock(return_value=b)
    controller = BankersController(use_case)

    result = await controller.get_banker(b.id)

    assert result.id == str(b.id)


@pytest.mark.asyncio
async def test_create_banker() -> None:
    b = build_banker_out_dto()
    eid = uuid4()
    use_case = AsyncMock()
    use_case.create_banker = AsyncMock(return_value=b)
    controller = BankersController(use_case)

    body = BankerCreateSchema(name='Banco Legal')
    result = await controller.create_banker(body, eid)

    assert result.name == b.name
    use_case.create_banker.assert_awaited_once()
    call_dto = use_case.create_banker.call_args[0][0]
    assert call_dto.name == 'Banco Legal'
    assert call_dto.created_by == eid


@pytest.mark.asyncio
async def test_update_banker() -> None:
    b = build_banker_out_dto(name='Atual')
    use_case = AsyncMock()
    use_case.update_banker = AsyncMock(return_value=b)
    controller = BankersController(use_case)

    body = BankerUpdateSchema(name='Novo Banco Aqui')
    result = await controller.update_banker(b.id, body)

    assert result.name == 'Atual'
    use_case.update_banker.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_banker() -> None:
    b = build_banker_out_dto()
    use_case = AsyncMock()
    use_case.delete_banker = AsyncMock(return_value=None)
    controller = BankersController(use_case)

    await controller.delete_banker(b.id)

    use_case.delete_banker.assert_awaited_once_with(b.id)
