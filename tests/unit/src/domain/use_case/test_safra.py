from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.domain.use_case.safra import SafraUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token() -> None:
    service = AsyncMock()
    service.get_token = AsyncMock(
        return_value=TokenResponse.model_validate({'token': 'abc'})
    )
    uc = SafraUseCase(service)
    out = await uc.get_token()
    assert out.token == 'abc'
    service.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_bankers() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='X',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    service = AsyncMock()
    service.get_bankers = AsyncMock(return_value=bankers)
    uc = SafraUseCase(service)
    out = await uc.get_bankers()
    assert out == bankers
    service.get_bankers.assert_awaited_once()
