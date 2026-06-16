from datetime import datetime
from unittest.mock import AsyncMock

import pytest
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
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.schemas.safra_calculation import (
    CalculationPortRefinInSchema,
    CalculationPortabilityInSchema,
    CalculationRefinInSchema,
    PortabilitySimulationInSchema,
    RefinSimulationInSchema,
)
from src.interface.api.v2.schemas.safra_leads import LeadReturnUploadItemInSchema
from src.interface.api.v2.schemas.safra_proposal_attachment import (
    ProposalAttachmentInSchema,
)

pytestmark = pytest.mark.unit


def _controller() -> tuple[SafraController, AsyncMock]:
    uc = AsyncMock()
    batch_uc = AsyncMock()
    return SafraController(uc, batch_uc), uc


@pytest.mark.asyncio
async def test_get_operational_guide_returns_schema() -> None:
    controller, uc = _controller()
    uc.get_operational_guide = AsyncMock(
        return_value=SafraOperationalGuideDto(idConvenio=1, idSetor=2),
    )
    out = await controller.get_operational_guide(1)
    assert out.idSetor == 2


@pytest.mark.asyncio
async def test_post_calculo_refin_returns_schema() -> None:
    controller, uc = _controller()
    uc.post_calculo_refin = AsyncMock(
        return_value=CalculationResponseDto(criticas=[], avisos=[]),
    )
    body = CalculationRefinInSchema(
        idConvenio=1,
        cpf=12345678901,
        comSeguro=False,
        valorMargemAdicional=0.0,
    )
    out = await controller.post_calculo_refin(body)
    assert out.criticas == []


@pytest.mark.asyncio
async def test_post_calculo_portabilidade_returns_schema() -> None:
    controller, uc = _controller()
    uc.post_calculo_portabilidade = AsyncMock(
        return_value=CalculationResponseDto(criticas=[], avisos=[]),
    )
    body = CalculationPortabilityInSchema(
        idConvenio=1,
        cpf=12345678901,
        comSeguro=False,
    )
    out = await controller.post_calculo_portabilidade(body)
    assert out.criticas == []


@pytest.mark.asyncio
async def test_post_calculo_portabilidade_refin_returns_schema() -> None:
    controller, uc = _controller()
    uc.post_calculo_portabilidade_refin = AsyncMock(
        return_value=CalculationPortRefinResponseDto(criticas=[], avisos=[]),
    )
    body = CalculationPortRefinInSchema(
        idConvenio=1,
        cpf=12345678901,
        simulacaoPortabilidade=PortabilitySimulationInSchema(
            valorParcelaContratoOrig=100.0,
            valorDivida=1000.0,
            prazoTotalContratoOrig=84,
            prazoRemanescenteContratoOrig=60,
        ),
        simulacaoRefin=RefinSimulationInSchema(),
    )
    out = await controller.post_calculo_portabilidade_refin(body)
    assert out.criticas == []


@pytest.mark.asyncio
async def test_list_interest_table_bands_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_interest_table_bands = AsyncMock(
        return_value=[SafraInterestTableBandDto(idFaixa=1)],
    )
    out = await controller.list_interest_table_bands(1)
    assert out[0].idFaixa == 1


@pytest.mark.asyncio
async def test_list_proposals_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_proposals = AsyncMock(return_value=[ProposalListItemDto(idProposta=1)])
    out = await controller.list_proposals(id_proposta=1, id_convenio=10)
    assert out[0].idProposta == 1


@pytest.mark.asyncio
async def test_post_proposal_attachment_delegates() -> None:
    controller, uc = _controller()
    body = ProposalAttachmentInSchema(
        idDocumento=1,
        nomeArquivo='doc.pdf',
        conteudoArquivo='data',
    )
    await controller.post_proposal_attachment(10, body)
    uc.post_proposal_attachment.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_leads_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_leads = AsyncMock(return_value=[LeadDto(idLead='L1')])
    out = await controller.list_leads()
    assert out[0].idLead == 'L1'


@pytest.mark.asyncio
async def test_download_leads_csv_returns_bytes() -> None:
    controller, uc = _controller()
    uc.download_leads_csv = AsyncMock(return_value=b'csv')
    out = await controller.download_leads_csv()
    assert out == b'csv'


@pytest.mark.asyncio
async def test_upload_leads_return_delegates() -> None:
    controller, uc = _controller()
    body = [LeadReturnUploadItemInSchema(idCliente=1)]
    await controller.upload_leads_return(body)
    uc.upload_leads_return.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_leads_return_file_delegates() -> None:
    controller, uc = _controller()
    await controller.upload_leads_return_file(b'data', 'file.csv')
    uc.upload_leads_return_file.assert_awaited_once_with(b'data', 'file.csv')


@pytest.mark.asyncio
async def test_get_proposal_flow_returns_schemas() -> None:
    controller, uc = _controller()
    uc.get_proposal_flow = AsyncMock(return_value=[ProposalFlowStepDto(idProposta=1)])
    out = await controller.get_proposal_flow(1)
    assert out[0].idProposta == 1


@pytest.mark.asyncio
async def test_get_formalization_tracking_returns_schemas() -> None:
    controller, uc = _controller()
    uc.get_formalization_tracking = AsyncMock(
        return_value=[FormalizationTrackingDto(idProposta=1, dtFase='2026-01-01')],
    )
    out = await controller.get_formalization_tracking(1)
    assert out[0].dtFase == '2026-01-01'


@pytest.mark.asyncio
async def test_approve_paradinha_returns_schema() -> None:
    controller, uc = _controller()
    uc.approve_paradinha = AsyncMock(
        return_value=ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    )
    out = await controller.approve_paradinha(1)
    assert out.idRetorno == 0


@pytest.mark.asyncio
async def test_cancel_paradinha_returns_schema() -> None:
    controller, uc = _controller()
    uc.cancel_paradinha = AsyncMock(
        return_value=ParadinhaResponseDto(idRetorno=0, dsRetorno='OK'),
    )
    out = await controller.cancel_paradinha(1)
    assert out.idRetorno == 0


@pytest.mark.asyncio
async def test_list_agencies_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_agencies = AsyncMock(
        return_value=[SafraAgencyDto(idBancoComercial=1, idAgenciaComercial=2)],
    )
    out = await controller.list_agencies()
    assert out[0].idAgenciaComercial == 2


@pytest.mark.asyncio
async def test_list_positions_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_positions = AsyncMock(return_value=[SafraPositionDto(idCargo=1)])
    out = await controller.list_positions(1)
    assert out[0].idCargo == 1


@pytest.mark.asyncio
async def test_list_employment_bonds_returns_schemas() -> None:
    controller, uc = _controller()
    uc.list_employment_bonds = AsyncMock(
        return_value=[SafraEmploymentBondDto(id=1)],
    )
    out = await controller.list_employment_bonds(1)
    assert out[0].id == 1


CONTRACT_CASES = [
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
    'method,args,items',
    CONTRACT_CASES,
    ids=[case[0] for case in CONTRACT_CASES],
)
async def test_contract_controller_methods(
    method: str,
    args: tuple,
    items: list,
) -> None:
    controller, uc = _controller()
    setattr(uc, method, AsyncMock(return_value=items))
    out = await getattr(controller, method)(*args)
    assert len(out) == 1
