from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.domain.service.safra import SafraService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_delegates_to_repository() -> None:
    repo = AsyncMock()
    repo.get_token = AsyncMock(
        return_value=TokenResponse.model_validate({'token': 'abc'})
    )
    service = SafraService(repo)
    out = await service.get_token()
    assert out.token == 'abc'
    repo.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_bankers_delegates_to_repository() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='X',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    repo = AsyncMock()
    repo.get_bankers = AsyncMock(return_value=bankers)
    service = SafraService(repo)
    out = await service.get_bankers()
    assert out == bankers
    repo.get_bankers.assert_awaited_once()
