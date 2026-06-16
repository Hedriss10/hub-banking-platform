from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    CalculationPortRefinResponseDto,
    PortabilitySimulationDto,
    RefinSimulationDto,
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
from src.domain.dtos.safra_leads import LeadReturnUploadItemDto
from src.domain.dtos.safra_proposal_tracking import (
    FormalizationTrackingDto,
    ParadinhaResponseDto,
    ProposalFlowStepDto,
)
from src.infrastructure.repositories.safra_external import SafraExternalRepository

pytestmark = pytest.mark.unit


def _mock_response(payload: object, *, content: bytes | None = None) -> MagicMock:
    mock_resp = MagicMock(spec=httpx.Response)
    if content is not None:
        mock_resp.content = content
    else:
        mock_resp.json.return_value = payload
    return mock_resp


LIST_CASES = [
    (
        'get_operational_guide',
        (1,),
        {'idConvenio': 1, 'idSetor': 2},
        SafraOperationalGuideDto,
    ),
    (
        'list_interest_table_bands',
        (1,),
        [{'idFaixa': 1}],
        SafraInterestTableBandDto,
    ),
    (
        'get_proposal_flow',
        (1,),
        [{'idProposta': 1}],
        ProposalFlowStepDto,
    ),
    (
        'get_formalization_tracking',
        (1,),
        [{'idProposta': 1, 'dtFase': '2026-01-01'}],
        FormalizationTrackingDto,
    ),
    ('list_agencies', (), [{'idBancoComercial': 1, 'idAgenciaComercial': 2}], SafraAgencyDto),
    ('list_positions', (1,), [{'idCargo': 1}], SafraPositionDto),
    ('list_employment_bonds', (1,), [{'id': 1}], SafraEmploymentBondDto),
    (
        'get_contracts_registration_by_cpf',
        ('123',),
        [{'nrCpfCliente': '123'}],
        ContractRegistrationDataDto,
    ),
    (
        'get_contracts_registration_by_date',
        ('2026-01-01',),
        [{'nrCpfCliente': '123'}],
        ContractRegistrationDataDto,
    ),
    (
        'get_contracts_registration_by_proposal',
        ('99',),
        [{'nrContrato': '99'}],
        ContractRegistrationDataDto,
    ),
    (
        'get_contracts_loan_by_cpf',
        ('123',),
        [{'nrCpfCliente': '123'}],
        ContractLoanDto,
    ),
    (
        'get_contracts_loan_by_date',
        ('2026-01-01',),
        [{'nrCpfCliente': '123'}],
        ContractLoanDto,
    ),
    (
        'get_contracts_loan_by_proposal',
        ('99',),
        [{'nrContrato': '99'}],
        ContractLoanDto,
    ),
    (
        'get_contracts_financial_by_cpf',
        ('123',),
        [{'nrCpfCliente': '123'}],
        ContractFinancialDto,
    ),
    (
        'get_contracts_financial_by_date',
        ('2026-01-01',),
        [{'nrCpfCliente': '123'}],
        ContractFinancialDto,
    ),
    (
        'get_contracts_financial_by_proposal',
        ('99',),
        [{'nrContrato': '99'}],
        ContractFinancialDto,
    ),
    (
        'get_contracts_status_by_date',
        ('2026-01-01',),
        [{'nrCpfCliente': '123', 'qtPendencias': 0}],
        ContractStatusDto,
    ),
    (
        'get_contracts_status_by_proposal',
        ('99',),
        [{'nrContrato': '99', 'qtPendencias': 0}],
        ContractStatusDto,
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'repo_method,args,payload,model',
    LIST_CASES,
    ids=[case[0] for case in LIST_CASES],
)
async def test_repository_maps_list_or_object(
    repo_method: str,
    args: tuple,
    payload: object,
    model: type,
) -> None:
    repo = SafraExternalRepository()
    setattr(repo.api, repo_method, AsyncMock(return_value=_mock_response(payload)))

    out = await getattr(repo, repo_method)(*args)

    if isinstance(payload, dict):
        assert isinstance(out, model)
    else:
        assert len(out) == 1
        assert isinstance(out[0], model)


@pytest.mark.asyncio
async def test_post_calculo_portabilidade_maps_response() -> None:
    dto = CalculationPortabilityRequestDto(
        idConvenio=1,
        cpf=12345678901,
        comSeguro=False,
    )
    repo = SafraExternalRepository()
    repo.api.post_calculo_portabilidade = AsyncMock(
        return_value=_mock_response({'criticas': [], 'avisos': []}),
    )
    out = await repo.post_calculo_portabilidade(dto)
    assert out.criticas == []


@pytest.mark.asyncio
async def test_post_calculo_portabilidade_refin_maps_response() -> None:
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
    repo = SafraExternalRepository()
    repo.api.post_calculo_portabilidade_refin = AsyncMock(
        return_value=_mock_response({'criticas': [], 'avisos': []}),
    )
    out = await repo.post_calculo_portabilidade_refin(dto)
    assert isinstance(out, CalculationPortRefinResponseDto)


@pytest.mark.asyncio
async def test_download_leads_csv_returns_content() -> None:
    repo = SafraExternalRepository()
    repo.api.download_leads_csv = AsyncMock(
        return_value=_mock_response(None, content=b'csv-data'),
    )
    out = await repo.download_leads_csv()
    assert out == b'csv-data'


@pytest.mark.asyncio
async def test_upload_leads_return_delegates() -> None:
    items = [LeadReturnUploadItemDto(idCliente=1)]
    repo = SafraExternalRepository()
    repo.api.upload_leads_return = AsyncMock(return_value=_mock_response({}))
    await repo.upload_leads_return(items)
    repo.api.upload_leads_return.assert_awaited_once_with(items)


@pytest.mark.asyncio
async def test_upload_leads_return_file_delegates() -> None:
    repo = SafraExternalRepository()
    repo.api.upload_leads_return_file = AsyncMock(return_value=_mock_response({}))
    await repo.upload_leads_return_file(b'data', 'file.csv')
    repo.api.upload_leads_return_file.assert_awaited_once_with(b'data', 'file.csv')


@pytest.mark.asyncio
async def test_approve_paradinha_maps_response() -> None:
    repo = SafraExternalRepository()
    repo.api.approve_paradinha = AsyncMock(
        return_value=_mock_response({'idRetorno': 0, 'dsRetorno': 'OK'}),
    )
    out = await repo.approve_paradinha(1)
    assert isinstance(out, ParadinhaResponseDto)
    assert out.idRetorno == 0


@pytest.mark.asyncio
async def test_cancel_paradinha_maps_response() -> None:
    repo = SafraExternalRepository()
    repo.api.cancel_paradinha = AsyncMock(
        return_value=_mock_response({'idRetorno': 0, 'dsRetorno': 'OK'}),
    )
    out = await repo.cancel_paradinha(1)
    assert isinstance(out, ParadinhaResponseDto)
