from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    CalculationPortRefinResponseDto,
    CalculationRefinRequestDto,
    CalculationRequestDto,
    CalculationResponseDto,
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
from src.domain.dtos.safra_formalization_link import FormalizationLinkQueryDto
from src.domain.dtos.safra_leads import LeadDto, LeadReturnUploadItemDto
from src.domain.dtos.safra_proposal_attachment import ProposalAttachmentDto
from src.domain.dtos.safra_proposal_tracking import (
    FormalizationTrackingDto,
    ParadinhaResponseDto,
    ProposalFlowStepDto,
    ProposalListItemDto,
    ProposalListQueryDto,
)
from src.domain.service.safra import SafraService
from src.domain.use_case.safra import SafraUseCase

pytestmark = pytest.mark.unit

_REFIN_DTO = CalculationRefinRequestDto(
    idConvenio=1,
    cpf=12345678901,
    comSeguro=False,
    valorMargemAdicional=0.0,
)
_PORT_DTO = CalculationPortabilityRequestDto(
    idConvenio=1,
    cpf=12345678901,
    comSeguro=False,
)
_PORT_REFIN_DTO = CalculationPortRefinRequestDto(
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
_ATTACHMENT_DTO = ProposalAttachmentDto(
    idDocumento=1,
    nomeArquivo='doc.pdf',
    conteudoArquivo='data',
)
_LEAD_RETURN = [LeadReturnUploadItemDto(idCliente=1)]

DELEGATION_CASES = [
    (
        'get_operational_guide',
        (1,),
        SafraOperationalGuideDto(idConvenio=1, idSetor=2),
    ),
    (
        'post_calculo_refin',
        (_REFIN_DTO,),
        CalculationResponseDto(criticas=[], avisos=[]),
    ),
    (
        'post_calculo_portabilidade',
        (_PORT_DTO,),
        CalculationResponseDto(criticas=[], avisos=[]),
    ),
    (
        'post_calculo_portabilidade_refin',
        (_PORT_REFIN_DTO,),
        CalculationPortRefinResponseDto(criticas=[], avisos=[]),
    ),
    (
        'list_interest_table_bands',
        (1,),
        [SafraInterestTableBandDto(idFaixa=1)],
    ),
    (
        'list_proposals',
        (ProposalListQueryDto(id_proposta=1),),
        [ProposalListItemDto(idProposta=1)],
    ),
    ('list_leads', (), [LeadDto(idLead='L1')]),
    ('download_leads_csv', (), b'csv'),
    (
        'get_proposal_formalization_link',
        (FormalizationLinkQueryDto(idProposta=1),),
        [],
    ),
    ('get_proposal_flow', (1,), [ProposalFlowStepDto(idProposta=1)]),
    (
        'get_formalization_tracking',
        (1,),
        [FormalizationTrackingDto(idProposta=1, dtFase='2026-01-01')],
    ),
    (
        'approve_paradinha',
        (1,),
        ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    ),
    (
        'cancel_paradinha',
        (1,),
        ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    ),
    ('list_agencies', (), [SafraAgencyDto(idBancoComercial=1, idAgenciaComercial=2)]),
    ('list_positions', (1,), [SafraPositionDto(idCargo=1)]),
    ('list_employment_bonds', (1,), [SafraEmploymentBondDto(id=1)]),
    (
        'get_contracts_registration_by_cpf',
        ('123',),
        [ContractRegistrationDataDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_registration_by_date',
        ('2026-01-01',),
        [ContractRegistrationDataDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_registration_by_proposal',
        ('99',),
        [ContractRegistrationDataDto(nrContrato='99')],
    ),
    (
        'get_contracts_loan_by_cpf',
        ('123',),
        [ContractLoanDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_loan_by_date',
        ('2026-01-01',),
        [ContractLoanDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_loan_by_proposal',
        ('99',),
        [ContractLoanDto(nrContrato='99')],
    ),
    (
        'get_contracts_financial_by_cpf',
        ('123',),
        [ContractFinancialDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_financial_by_date',
        ('2026-01-01',),
        [ContractFinancialDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_financial_by_proposal',
        ('99',),
        [ContractFinancialDto(nrContrato='99')],
    ),
    (
        'get_contracts_status_by_cpf',
        ('123',),
        [ContractStatusDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_status_by_date',
        ('2026-01-01',),
        [ContractStatusDto(nrCpfCliente='123')],
    ),
    (
        'get_contracts_status_by_proposal',
        ('99',),
        [ContractStatusDto(nrContrato='99')],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method_name,args,expected',
    DELEGATION_CASES,
    ids=[case[0] for case in DELEGATION_CASES],
)
async def test_service_delegates_to_repository(
    method_name: str,
    args: tuple,
    expected: object,
) -> None:
    repo = AsyncMock()
    getattr(repo, method_name).return_value = expected
    service = SafraService(repo)

    result = await getattr(service, method_name)(*args)

    assert result == expected
    getattr(repo, method_name).assert_awaited_once_with(*args)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method_name,args,expected',
    DELEGATION_CASES,
    ids=[f'uc_{case[0]}' for case in DELEGATION_CASES],
)
async def test_use_case_delegates_to_service(
    method_name: str,
    args: tuple,
    expected: object,
) -> None:
    service = AsyncMock()
    getattr(service, method_name).return_value = expected
    use_case = SafraUseCase(service)

    result = await getattr(use_case, method_name)(*args)

    assert result == expected
    getattr(service, method_name).assert_awaited_once_with(*args)


@pytest.mark.asyncio
async def test_service_post_proposal_attachment_delegates() -> None:
    repo = AsyncMock()
    service = SafraService(repo)
    await service.post_proposal_attachment(10, _ATTACHMENT_DTO)
    repo.post_proposal_attachment.assert_awaited_once_with(10, _ATTACHMENT_DTO)


@pytest.mark.asyncio
async def test_service_upload_leads_return_delegates() -> None:
    repo = AsyncMock()
    service = SafraService(repo)
    await service.upload_leads_return(_LEAD_RETURN)
    repo.upload_leads_return.assert_awaited_once_with(_LEAD_RETURN)


@pytest.mark.asyncio
async def test_service_upload_leads_return_file_delegates() -> None:
    repo = AsyncMock()
    service = SafraService(repo)
    await service.upload_leads_return_file(b'data', 'file.csv')
    repo.upload_leads_return_file.assert_awaited_once_with(b'data', 'file.csv')


@pytest.mark.asyncio
async def test_use_case_post_proposal_attachment_delegates() -> None:
    service = AsyncMock()
    use_case = SafraUseCase(service)
    await use_case.post_proposal_attachment(10, _ATTACHMENT_DTO)
    service.post_proposal_attachment.assert_awaited_once_with(10, _ATTACHMENT_DTO)


@pytest.mark.asyncio
async def test_use_case_upload_leads_return_delegates() -> None:
    service = AsyncMock()
    use_case = SafraUseCase(service)
    await use_case.upload_leads_return(_LEAD_RETURN)
    service.upload_leads_return.assert_awaited_once_with(_LEAD_RETURN)


@pytest.mark.asyncio
async def test_use_case_upload_leads_return_file_delegates() -> None:
    service = AsyncMock()
    use_case = SafraUseCase(service)
    await use_case.upload_leads_return_file(b'data', 'file.csv')
    service.upload_leads_return_file.assert_awaited_once_with(b'data', 'file.csv')
