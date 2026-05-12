from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.infrastructure.repositories.safra_external import SafraExternalRepository

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_maps_response_json() -> None:
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {'token': 'jwt-here'}
    repo.api.get_token = AsyncMock(return_value=mock_resp)

    out = await repo.get_token()

    assert isinstance(out, TokenResponse)
    assert out.token == 'jwt-here'


@pytest.mark.asyncio
async def test_get_bankers_parses_rows() -> None:
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'data': [
            {
                'codigoBanco': 1,
                'nomeBanco': 'B',
                'cnpj': 12345678000190,
                'ispb': 12345678,
            }
        ]
    }
    repo.api.get_bankers = AsyncMock(return_value=mock_resp)

    out = await repo.get_bankers()

    assert len(out) == 1
    assert isinstance(out[0], BankerResponse)
    assert out[0].nomeBanco == 'B'


@pytest.mark.asyncio
async def test_repository_instantiation_creates_api() -> None:
    with patch(
        'src.infrastructure.repositories.safra_external.SafraApi',
    ) as mock_cls:
        repo = SafraExternalRepository()
        mock_cls.assert_called_once()
        assert repo.api is mock_cls.return_value
