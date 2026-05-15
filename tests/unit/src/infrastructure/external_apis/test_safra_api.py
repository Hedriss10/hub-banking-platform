from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.core.exceptions.custom import InfrastructureException
from src.domain.dtos.safra import MargemBpoDto
from src.infrastructure.external_apis.safra import SafraApi

pytestmark = pytest.mark.unit


@pytest.fixture
def safra_api() -> SafraApi:
    return SafraApi()


def test_access_token_from_valid(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'secret'},
    )
    assert safra_api._access_token_from(resp) == 'secret'


@pytest.mark.parametrize(
    'payload',
    [
        {},
        {'token': ''},
        {'token': None},
    ],
)
def test_access_token_from_invalid_dict(
    safra_api: SafraApi,
    payload: dict,
) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json=payload,
    )
    with pytest.raises(InfrastructureException):
        safra_api._access_token_from(resp)


def test_access_token_from_non_dict_json(safra_api: SafraApi) -> None:
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = ['not', 'a', 'dict']
    with pytest.raises(InfrastructureException):
        safra_api._access_token_from(resp)


@pytest.mark.asyncio
async def test_get_token_posts_to_token_url(safra_api: SafraApi) -> None:
    ok = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/api/v1/Token'),
        json={'token': 't'},
    )
    mock_req = AsyncMock(return_value=ok)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_token()
    assert out.json()['token'] == 't'
    mock_req.assert_awaited_once()
    call = mock_req.await_args[0][0]
    assert call['method'] == 'POST'
    assert call['url'] == '/api/v1/Token'


@pytest.mark.asyncio
async def test_get_bankers_uses_bearer_from_token(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    banks_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/banks'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return banks_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_bankers()

    assert urls == ['/api/v1/Token', '/api/v1/Banco']
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'


@pytest.mark.asyncio
async def test_get_margem_bpo_posts_consulta_margem(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    margem_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/margem'),
        json={'cpf': '1', 'margem': 0.0},
    )

    async def _req(data: dict):
        if data['url'] == '/api/v1/Token':
            return token_resp
        return margem_resp

    mock_req = AsyncMock(side_effect=_req)
    dto = MargemBpoDto(convenio=1, cpf='12345678901', idProduto=2, matricula='M')
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_margem_bpo(dto)

    assert out.json()['margem'] == 0.0
    second = mock_req.await_args_list[1][0][0]
    assert second['method'] == 'POST'
    assert second['url'] == '/api/v1/ConsultaMargem/Bpo'
    assert second['headers']['Authorization'] == 'Bearer abc'
    assert second['json'] == dto.model_dump()


@pytest.mark.asyncio
async def test_get_financial_agreements_uses_bearer_from_token(
    safra_api: SafraApi,
) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    financial_agreements_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/financial-agreements'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return financial_agreements_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_financial_agreements()
    assert urls == ['/api/v1/Token', '/api/v1/Convenio']
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'
