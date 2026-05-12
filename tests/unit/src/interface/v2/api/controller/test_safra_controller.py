from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.interface.api.v2.controller.safra import SafraController

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_returns_schema() -> None:
    uc = AsyncMock()
    uc.get_token = AsyncMock(return_value=TokenResponse.model_validate({'token': 'x'}))
    controller = SafraController(uc)
    out = await controller.get_token()
    assert out.token == 'x'
    uc.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_banks_returns_schemas() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='N',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    uc = AsyncMock()
    uc.get_bankers = AsyncMock(return_value=bankers)
    controller = SafraController(uc)
    out = await controller.list_banks()
    assert len(out) == 1
    assert out[0].nomeBanco == 'N'
