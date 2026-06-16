from unittest.mock import AsyncMock, patch

import httpx
import pytest
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    PortabilitySimulationDto,
    RefinSimulationDto,
)
from src.domain.dtos.safra_leads import LeadReturnUploadItemDto
from src.infrastructure.external_apis.safra import SafraApi

pytestmark = pytest.mark.unit

_TOKEN_RESP = httpx.Response(
    200,
    request=httpx.Request('POST', 'https://x/token'),
    json={'token': 'abc'},
)


def _auth_patch(safra_api: SafraApi, api_response: httpx.Response):
    async def _req(data: dict):
        if data['url'] == '/api/v1/Token':
            return _TOKEN_RESP
        return api_response

    return patch.object(safra_api, 'request', AsyncMock(side_effect=_req))


@pytest.mark.asyncio
async def test_url_with_query_empty_returns_base() -> None:
    assert SafraApi._url_with_query('/base', {}) == '/base'


@pytest.mark.asyncio
async def test_url_with_query_skips_none_values() -> None:
    url = SafraApi._url_with_query('/base', {'a': 1, 'b': None})
    assert url == '/base?a=1'


@pytest.mark.asyncio
async def test_get_operational_guide(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/guide'),
        json={'idConvenio': 1, 'idSetor': 2},
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.get_operational_guide(1)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()['idSetor'] == 2
    assert call['url'] == '/api/v1/Convenio/RoteiroOperacional/1'


@pytest.mark.asyncio
async def test_list_interest_table_bands(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/bands'),
        json=[{'idFaixa': 1}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.list_interest_table_bands(5)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()[0]['idFaixa'] == 1
    assert call['url'] == '/api/v1/TabelaJuros/Faixas/5'


@pytest.mark.asyncio
async def test_post_calculo_portabilidade(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/calc'),
        json={'criticas': []},
    )
    dto = CalculationPortabilityRequestDto(
        idConvenio=1,
        cpf=12345678901,
        comSeguro=False,
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.post_calculo_portabilidade(dto)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()['criticas'] == []
    assert call['url'] == '/api/v1/Calculo/Portabilidade'


@pytest.mark.asyncio
async def test_post_calculo_portabilidade_refin(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/calc'),
        json={'criticas': []},
    )
    dto = CalculationPortRefinRequestDto(
        idConvenio=1,
        cpf=12345678901,
        simulacaoPortabilidade=PortabilitySimulationDto(
            valorParcelaContratoOrig=100.0,
            valorDivida=1000.0,
            prazoTotalContratoOrig=84,
            prazoRemanescenteContratoOrig=60,
        ),
        simulacaoRefin=RefinSimulationDto(),
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.post_calculo_portabilidade_refin(dto)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()['criticas'] == []
    assert call['url'] == '/api/v1/Calculo/PortabilidadeRefin'


@pytest.mark.asyncio
async def test_download_leads_csv(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/download'),
        content=b'idLead\nL1',
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.download_leads_csv()
        call = mock_req.await_args_list[1][0][0]
    assert out.content == b'idLead\nL1'
    assert call['url'] == '/api/v1/Lead/Download'


@pytest.mark.asyncio
async def test_upload_leads_return(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/upload'),
        json={},
    )
    items = [LeadReturnUploadItemDto(idCliente=1)]
    with _auth_patch(safra_api, resp) as mock_req:
        await safra_api.upload_leads_return(items)
        call = mock_req.await_args_list[1][0][0]
    assert call['url'] == '/api/v1/Lead/UploadRetorno'
    assert call['json'] == [{'idCliente': 1}]


@pytest.mark.asyncio
async def test_upload_leads_return_file_multipart(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/upload-file'),
        json={},
    )
    with _auth_patch(safra_api, resp) as mock_req:
        await safra_api.upload_leads_return_file(b'data', 'retorno.csv')
        call = mock_req.await_args_list[1][0][0]
    assert call['url'] == '/api/v1/Lead/UploadArquivoRetorno'
    assert call['files'] == {'file': ('retorno.csv', b'data')}


@pytest.mark.asyncio
async def test_get_proposal_flow(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/flow'),
        json=[{'idProposta': 1}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.get_proposal_flow(1)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()[0]['idProposta'] == 1
    assert call['url'] == '/api/v1/FluxoProposta?idProposta=1'


@pytest.mark.asyncio
async def test_get_formalization_tracking(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/tracking'),
        json=[{'idProposta': 1, 'dtFase': '2026-01-01'}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.get_formalization_tracking(1)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()[0]['dtFase'] == '2026-01-01'
    assert call['url'] == '/api/v1/AcompanhamentoFormalizacao?idProposta=1'


@pytest.mark.asyncio
async def test_approve_paradinha_without_json_body(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/approve'),
        json={'idRetorno': 0},
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.approve_paradinha(99)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()['idRetorno'] == 0
    assert call['url'] == '/api/v1/ParadinhaCorrespondente/aprova/99'
    assert 'json' not in call


@pytest.mark.asyncio
async def test_cancel_paradinha(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('POST', 'https://x/cancel'),
        json={'idRetorno': 0},
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.cancel_paradinha(99)
        call = mock_req.await_args_list[1][0][0]
    assert out.json()['idRetorno'] == 0
    assert call['url'] == '/api/v1/ParadinhaCorrespondente/cancela/99'


@pytest.mark.asyncio
async def test_list_agencies(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/agencies'),
        json=[{'idBancoComercial': 1, 'idAgenciaComercial': 2}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        out = await safra_api.list_agencies()
        call = mock_req.await_args_list[1][0][0]
    assert out.json()[0]['idBancoComercial'] == 1
    assert call['url'] == '/api/v1/Agencia'


@pytest.mark.asyncio
async def test_list_positions(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/positions'),
        json=[{'idCargo': 1}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        await safra_api.list_positions(3)
        call = mock_req.await_args_list[1][0][0]
    assert call['url'] == '/api/v1/Cargo/3'


@pytest.mark.asyncio
async def test_list_employment_bonds(safra_api: SafraApi) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/bonds'),
        json=[{'id': 1}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        await safra_api.list_employment_bonds(7)
        call = mock_req.await_args_list[1][0][0]
    assert call['url'] == '/api/v1/VinculoEmpregaticio/7'


CONTRACT_GET_CASES = [
    ('get_contracts_registration_by_cpf', '123', '/api/v1/ContratosDadosCadastrais/cpf/123'),
    ('get_contracts_registration_by_date', '2026-01-01', '/api/v1/ContratosDadosCadastrais/data/2026-01-01'),
    ('get_contracts_registration_by_proposal', '99', '/api/v1/ContratosDadosCadastrais/proposta/99'),
    ('get_contracts_loan_by_cpf', '123', '/api/v1/ContratosEmprestimo/cpf/123'),
    ('get_contracts_loan_by_date', '2026-01-01', '/api/v1/ContratosEmprestimo/data/2026-01-01'),
    ('get_contracts_loan_by_proposal', '99', '/api/v1/ContratosEmprestimo/proposta/99'),
    ('get_contracts_financial_by_cpf', '123', '/api/v1/ContratosFinanceiro/cpf/123'),
    ('get_contracts_financial_by_date', '2026-01-01', '/api/v1/ContratosFinanceiro/data/2026-01-01'),
    ('get_contracts_financial_by_proposal', '99', '/api/v1/ContratosFinanceiro/proposta/99'),
    ('get_contracts_status_by_date', '2026-01-01', '/api/v1/ContratosStatus/data/2026-01-01'),
    ('get_contracts_status_by_proposal', '99', '/api/v1/ContratosStatus/proposta/99'),
]


@pytest.fixture
def safra_api() -> SafraApi:
    return SafraApi()


@pytest.mark.asyncio
@pytest.mark.parametrize('method,arg,expected_url', CONTRACT_GET_CASES)
async def test_contract_get_endpoints(
    safra_api: SafraApi,
    method: str,
    arg: str,
    expected_url: str,
) -> None:
    resp = httpx.Response(
        200,
        request=httpx.Request('GET', 'https://x/contracts'),
        json=[{'nrCpfCliente': '123'}],
    )
    with _auth_patch(safra_api, resp) as mock_req:
        await getattr(safra_api, method)(arg)
        call = mock_req.await_args_list[1][0][0]
    assert call['url'] == expected_url
