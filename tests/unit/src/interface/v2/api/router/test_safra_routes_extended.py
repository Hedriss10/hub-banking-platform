from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from src.domain.dtos.safra_calculation import (
    CalculationPortRefinResponseDto,
    CalculationResponseDto,
)
from src.domain.dtos.safra_catalog import (
    SafraAgencyDto,
    SafraEmploymentBondDto,
    SafraInterestTableBandDto,
    SafraOperationalGuideDto,
    SafraPositionDto,
)
from src.domain.dtos.safra_contracts import (
    ContractFinancialDto,
    ContractLoanDto,
    ContractRegistrationDataDto,
    ContractStatusDto,
)
from src.domain.dtos.safra_leads import LeadDto
from src.domain.dtos.safra_proposal_tracking import (
    FormalizationTrackingDto,
    ParadinhaResponseDto,
    ProposalFlowStepDto,
    ProposalListItemDto,
)
from starlette import status

pytestmark = pytest.mark.unit

_BASE = '/api/v2/safra'


@pytest.mark.asyncio
async def test_post_calculation_refin(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.post_calculo_refin = AsyncMock(
        return_value=CalculationResponseDto(criticas=[], avisos=[]),
    )
    response = await async_safra_client.post(
        f'{_BASE}/calculation/refin',
        json={
            'idConvenio': 1,
            'cpf': 12345678901,
            'comSeguro': False,
            'valorMargemAdicional': 0.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    mock_safra_use_case.post_calculo_refin.assert_awaited_once()


@pytest.mark.asyncio
async def test_post_calculation_portability(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.post_calculo_portabilidade = AsyncMock(
        return_value=CalculationResponseDto(criticas=[], avisos=[]),
    )
    response = await async_safra_client.post(
        f'{_BASE}/calculation/portability',
        json={'idConvenio': 1, 'cpf': 12345678901, 'comSeguro': False},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_post_calculation_portability_refin(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.post_calculo_portabilidade_refin = AsyncMock(
        return_value=CalculationPortRefinResponseDto(criticas=[], avisos=[]),
    )
    response = await async_safra_client.post(
        f'{_BASE}/calculation/portability-refin',
        json={
            'idConvenio': 1,
            'cpf': 12345678901,
            'simulacaoPortabilidade': {
                'valorParcelaContratoOrig': 100.0,
                'valorDivida': 1000.0,
                'prazoTotalContratoOrig': 84,
                'prazoRemanescenteContratoOrig': 60,
            },
            'simulacaoRefin': {},
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_post_proposal_attachment(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.post_proposal_attachment = AsyncMock(return_value=None)
    response = await async_safra_client.post(
        f'{_BASE}/proposals/10/attachments',
        json={
            'idDocumento': 1,
            'nomeArquivo': 'doc.pdf',
            'conteudoArquivo': 'data',
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_leads(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_leads = AsyncMock(return_value=[LeadDto(idLead='L1')])
    response = await async_safra_client.get(f'{_BASE}/leads')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['idLead'] == 'L1'


@pytest.mark.asyncio
async def test_get_leads_download(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.download_leads_csv = AsyncMock(return_value=b'idLead\nL1')
    response = await async_safra_client.get(f'{_BASE}/leads/download')
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'idLead\nL1'


@pytest.mark.asyncio
async def test_post_leads_return_upload(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.upload_leads_return = AsyncMock(return_value=None)
    response = await async_safra_client.post(
        f'{_BASE}/leads/return-upload',
        json=[{'idCliente': 1}],
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_post_leads_return_upload_file(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.upload_leads_return_file = AsyncMock(return_value=None)
    response = await async_safra_client.post(
        f'{_BASE}/leads/return-upload/file',
        files={'file': ('retorno.csv', b'data', 'text/csv')},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_operational_guide(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.get_operational_guide = AsyncMock(
        return_value=SafraOperationalGuideDto(idConvenio=1, idSetor=2),
    )
    response = await async_safra_client.get(
        f'{_BASE}/financial-agreements/1/operational-guide',
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_interest_table_bands(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_interest_table_bands = AsyncMock(
        return_value=[SafraInterestTableBandDto(idFaixa=1)],
    )
    response = await async_safra_client.get(f'{_BASE}/tables/1/bands')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_catalog_agencies(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_agencies = AsyncMock(
        return_value=[SafraAgencyDto(idBancoComercial=1, idAgenciaComercial=2)],
    )
    response = await async_safra_client.get(f'{_BASE}/catalog/agencies')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_catalog_positions(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_positions = AsyncMock(
        return_value=[SafraPositionDto(idCargo=1)],
    )
    response = await async_safra_client.get(f'{_BASE}/catalog/positions/1')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_catalog_employment_bonds(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_employment_bonds = AsyncMock(
        return_value=[SafraEmploymentBondDto(id=1)],
    )
    response = await async_safra_client.get(f'{_BASE}/catalog/employment-bonds/1')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_proposals_search(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.list_proposals = AsyncMock(
        return_value=[ProposalListItemDto(idProposta=1)],
    )
    response = await async_safra_client.get(
        f'{_BASE}/proposals/search',
        params={'id_proposta': 1},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_proposal_flow(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.get_proposal_flow = AsyncMock(
        return_value=[ProposalFlowStepDto(idProposta=1)],
    )
    response = await async_safra_client.get(f'{_BASE}/proposals/1/flow')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_formalization_tracking(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.get_formalization_tracking = AsyncMock(
        return_value=[FormalizationTrackingDto(idProposta=1, dtFase='2026-01-01')],
    )
    response = await async_safra_client.get(
        f'{_BASE}/proposals/1/formalization-tracking',
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_post_paradinha_approve(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.approve_paradinha = AsyncMock(
        return_value=ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    )
    response = await async_safra_client.post(f'{_BASE}/paradinha/1/approve')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_post_paradinha_cancel(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.cancel_paradinha = AsyncMock(
        return_value=ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    )
    response = await async_safra_client.post(f'{_BASE}/paradinha/1/cancel')
    assert response.status_code == status.HTTP_200_OK


CONTRACT_ROUTES = [
    (
        '/contracts/registration-data/cpf/123',
        'get_contracts_registration_by_cpf',
        [ContractRegistrationDataDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/registration-data/date/2026-01-01',
        'get_contracts_registration_by_date',
        [ContractRegistrationDataDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/registration-data/proposal/99',
        'get_contracts_registration_by_proposal',
        [ContractRegistrationDataDto(nrContrato='99')],
    ),
    (
        '/contracts/loan/cpf/123',
        'get_contracts_loan_by_cpf',
        [ContractLoanDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/loan/date/2026-01-01',
        'get_contracts_loan_by_date',
        [ContractLoanDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/loan/proposal/99',
        'get_contracts_loan_by_proposal',
        [ContractLoanDto(nrContrato='99')],
    ),
    (
        '/contracts/financial/cpf/123',
        'get_contracts_financial_by_cpf',
        [ContractFinancialDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/financial/date/2026-01-01',
        'get_contracts_financial_by_date',
        [ContractFinancialDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/financial/proposal/99',
        'get_contracts_financial_by_proposal',
        [ContractFinancialDto(nrContrato='99')],
    ),
    (
        '/contracts/status/cpf/123',
        'get_contracts_status_by_cpf',
        [ContractStatusDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/status/date/2026-01-01',
        'get_contracts_status_by_date',
        [ContractStatusDto(nrCpfCliente='123')],
    ),
    (
        '/contracts/status/proposal/99',
        'get_contracts_status_by_proposal',
        [ContractStatusDto(nrContrato='99')],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'path,use_case_method,return_value',
    CONTRACT_ROUTES,
    ids=[route[1] for route in CONTRACT_ROUTES],
)
async def test_contract_routes(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
    path: str,
    use_case_method: str,
    return_value: list,
) -> None:
    setattr(mock_safra_use_case, use_case_method, AsyncMock(return_value=return_value))
    response = await async_safra_client.get(f'{_BASE}{path}')
    assert response.status_code == status.HTTP_200_OK
