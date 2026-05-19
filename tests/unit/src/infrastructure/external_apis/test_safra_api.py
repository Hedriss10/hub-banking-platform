from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.core.exceptions.custom import InfrastructureException
from src.domain.dtos.safra import MargemBpoDto
from src.domain.dtos.safra_credit_ligth_house import CreditLighthouseDto
from src.domain.dtos.safra_proposal import ProposalDto
from src.infrastructure.external_apis.safra import SafraApi
from tests.fixtures.safra_proposal_min import minimal_safra_proposal_payload

pytestmark = pytest.mark.unit

_PROPOSTAS_NOVO_STUB_ID = 12


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


@pytest.mark.asyncio
async def test_post_credit_lighthouse_posts_farol_credito(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    farol_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/farol'),
        json={'decisaoFarol': 1},
    )

    async def _req(data: dict):
        if data['url'] == '/api/v1/Token':
            return token_resp
        return farol_resp

    dto = CreditLighthouseDto(idConvenio=1, idTipoProduto=5, cpf=9999999909)
    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.post_credit_lighthouse(dto)

    assert out.json()['decisaoFarol'] == 1
    second = mock_req.await_args_list[1][0][0]
    assert second['method'] == 'POST'
    assert second['url'] == '/api/v1/FarolCredito'
    assert second['headers']['Authorization'] == 'Bearer abc'
    assert second['json'] == dto.model_dump()


@pytest.mark.asyncio
async def test_list_safra_tables_uses_bearer_from_token(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    safra_tables_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/tables'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return safra_tables_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.list_safra_tables(1)
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'


@pytest.mark.asyncio
async def test_post_safra_proposal_posts_propostas_novo(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    proposal_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/propostas'),
        json={'idProposta': _PROPOSTAS_NOVO_STUB_ID},
    )
    dto_in = ProposalDto.model_validate(minimal_safra_proposal_payload())

    async def _req(data: dict):
        if data['url'] == '/api/v1/Token':
            return token_resp
        return proposal_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.post_safra_proposal(dto_in)

    assert out.json()['idProposta'] == _PROPOSTAS_NOVO_STUB_ID
    proposal_call = mock_req.await_args_list[1][0][0]
    assert proposal_call['method'] == 'POST'
    assert proposal_call['url'] == '/api/v1/Propostas/Novo'
    assert proposal_call['headers']['Authorization'] == 'Bearer abc'
    assert proposal_call['json'] == dto_in.model_dump()


@pytest.mark.asyncio
async def test_get_employing_bodies_uses_bearer_from_token(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    employing_bodies_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/employing-bodies'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return employing_bodies_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_employing_bodies(1)
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'
    assert second_call['url'] == '/api/v1/OrgaoEmpregador/1'


@pytest.mark.asyncio
async def test_get_professions_uses_bearer_from_token(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    professions_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/professions'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return professions_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_professions(1)
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'
    assert second_call['url'] == '/api/v1/Profissao/1'


@pytest.mark.asyncio
async def test_get_legal_regime_uses_bearer_from_token(safra_api: SafraApi) -> None:
    token_resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/token'),
        json={'token': 'abc'},
    )
    legal_regime_resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/RegimeJuridico'),
        json=[],
    )
    urls: list[str] = []

    async def _req(data: dict):
        urls.append(data['url'])
        if data['method'] == 'POST':
            return token_resp
        return legal_regime_resp

    mock_req = AsyncMock(side_effect=_req)
    with patch.object(safra_api, 'request', mock_req):
        out = await safra_api.get_legal_regime(1)
    assert out.json() == []
    second_call = mock_req.await_args_list[1][0][0]
    assert second_call['headers']['Authorization'] == 'Bearer abc'
    assert second_call['url'] == '/api/v1/RegimeJuridico/1'
