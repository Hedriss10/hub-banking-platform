from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, Response, UploadFile, status

from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.safra import SafraControllerDep
from src.interface.api.v2.schemas.employee_situation import EmployeeSituationSchema
from src.interface.api.v2.schemas.safra import (
    BankerOutSchema,
    MargemBpoInSchema,
    MargemBpoOutSchema,
    SafraBatchJobIdsOutSchema,
    SafraBatchJobStatusOutSchema,
    SafraBatchUploadOutSchema,
    TokenOutSchema,
)
from src.interface.api.v2.schemas.safra_calculation import (
    CalculationInSchema,
    CalculationOutSchema,
    CalculationPortabilityInSchema,
    CalculationPortRefinInSchema,
    CalculationPortRefinOutSchema,
    CalculationRefinInSchema,
)
from src.interface.api.v2.schemas.safra_catalog import (
    SafraAgencyOutSchema,
    SafraEmploymentBondOutSchema,
    SafraInterestTableBandOutSchema,
    SafraOperationalGuideOutSchema,
    SafraPositionOutSchema,
)
from src.interface.api.v2.schemas.safra_contracts import (
    ContractFinancialOutSchema,
    ContractLoanOutSchema,
    ContractRegistrationDataOutSchema,
    ContractStatusOutSchema,
)
from src.interface.api.v2.schemas.safra_credit_ligth_house import (
    CreditLighthouseInSchema,
    CreditLighthouseOutSchema,
)
from src.interface.api.v2.schemas.safra_employing_body import SafraEmployingBodySchema
from src.interface.api.v2.schemas.safra_financial_agreements import (
    FinancialAgreementOutSchema,
)
from src.interface.api.v2.schemas.safra_formalization_link import (
    FormalizationLinkOutSchema,
)
from src.interface.api.v2.schemas.safra_leads import (
    LeadOutSchema,
    LeadReturnUploadItemInSchema,
)
from src.interface.api.v2.schemas.safra_professions import SafraProfessionsSchema
from src.interface.api.v2.schemas.safra_proposal import (
    ProposalResponseSchema,
    ProposalSchema,
)
from src.interface.api.v2.schemas.safra_proposal_attachment import (
    ProposalAttachmentInSchema,
)
from src.interface.api.v2.schemas.safra_proposal_tracking import (
    FormalizationTrackingOutSchema,
    ParadinhaOutSchema,
    ProposalFlowStepOutSchema,
    ProposalListItemOutSchema,
)
from src.interface.api.v2.schemas.safra_regime_legal import SafraRegimeLegalSchema
from src.interface.api.v2.schemas.safra_tables import SafraTablesOutSchema

tags_metadata = {
    'name': 'Safra',
    'description': ('Integration with the Safra external API.'),
}


router = APIRouter(
    prefix='/safra',
    tags=[tags_metadata['name']],
)


@router.post(
    '/token',
    response_model=TokenOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Get Safra token',
    description=(
        'Requires Authorization: Bearer header with the employee access token.'
    ),
)
async def post_safra_token(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> TokenOutSchema:
    return await controller.get_token()


@router.get(
    '/banks',
    response_model=List[BankerOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List banks (Safra)',
    description=(
        'Requires Authorization: Bearer (employee JWT). '
        'The Safra API token is obtained on the server when this endpoint runs.'
    ),
)
async def list_safra_banks(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[BankerOutSchema]:
    return await controller.list_banks()


@router.post(
    '/margin/bpo',
    response_model=MargemBpoOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Consult margin (BPO)',
    description=(
        'Margin enquiry via Safra ConsultaMargem/Bpo. '
        'Requires Authorization: Bearer (employee JWT); '
        'Safra token is obtained server-side. '
        'Send `cpf` as a string to preserve leading zeros.'
    ),
)
async def post_safra_margin_bpo(
    body: MargemBpoInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> MargemBpoOutSchema:
    return await controller.consult_margem_bpo(body)


@router.get(
    '/batch/search/job-ids',
    response_model=SafraBatchJobIdsOutSchema,
    status_code=status.HTTP_200_OK,
    summary='List distinct batch_job_id (Postgres)',
    description=(
        'Returns identifiers for jobs that have at least one row persisted '
        'in `safra_batch_search` (excludes rows marked deleted).'
    ),
)
async def get_safra_batch_search_job_ids(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> SafraBatchJobIdsOutSchema:
    return await controller.list_persisted_batch_job_ids()


@router.post(
    '/batch/search/upload',
    response_model=SafraBatchUploadOutSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary='Upload CSV — Safra batch margin enquiry',
    description=(
        'Accepts a UTF-8 CSV with headers (convenio, idProduto, cpf, matricula; '
        'optional phones phone_one … phone_five). '
        'Processing runs in the background; poll GET /batch/search/{job_id}/status. '
        'Requires REDIS_URL to be configured.'
    ),
)
async def post_safra_batch_search_upload(
    background_tasks: BackgroundTasks,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    file: UploadFile = File(..., description='UTF-8 CSV file'),
) -> SafraBatchUploadOutSchema:
    return await controller.upload_batch_search_csv(file, background_tasks)


@router.get(
    '/batch/search/{job_id}/status',
    response_model=SafraBatchJobStatusOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Safra batch job status',
    description=('Frontend polling; job state lives in Redis until it expires.'),
)
async def get_safra_batch_search_status(
    job_id: UUID,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> SafraBatchJobStatusOutSchema:
    return await controller.get_batch_job_status(job_id)


@router.get(
    '/batch/search/{batch_job_id}/export',
    status_code=status.HTTP_200_OK,
    summary='Export batch results as CSV',
    description=(
        'UTF-8 CSV (with BOM), delimiter `;`, same payload persisted by the worker '
        '`batch_job_id` matches the upload response `job_id`.'
    ),
)
async def get_safra_batch_search_export(
    batch_job_id: UUID,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    payload = await controller.export_batch_job_results_csv(batch_job_id)
    disposition = f'attachment; filename="safra-batch-{batch_job_id}.csv"'
    return Response(
        content=payload,
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': disposition},
    )


@router.delete(
    '/batch/search/{batch_job_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Hard-delete batch rows (Postgres)',
    description=(
        'Runs SQL `DELETE` on `safra_batch_search` for the given `batch_job_id` '
        '(permanent removal — not soft delete via `is_deleted`). '
        'Does not change Redis job state; **404** when no rows exist for this UUID.'
    ),
)
async def delete_safra_batch_search_job(
    batch_job_id: UUID,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.delete_batch_job_search_records(batch_job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '/financial-agreements',
    response_model=List[FinancialAgreementOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List financial agreements',
    description='List financial agreements from Safra',
)
async def get_safra_financial_agreements(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[FinancialAgreementOutSchema]:
    return await controller.list_financial_agreements()


@router.post(
    '/credit-lighthouse',
    response_model=List[CreditLighthouseOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Post credit lighthouse',
    description='Post credit lighthouse from Safra',
)
async def post_safra_credit_lighthouse(
    body: CreditLighthouseInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[CreditLighthouseOutSchema]:
    return await controller.post_credit_lighthouse(body)


@router.post(
    '/calculation/new',
    response_model=CalculationOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Simulate consignado values (Novo)',
    description=(
        'Segundo passo do fluxo de digitação de proposta consignado (FAQ Safra): '
        'FarolCredito → Calculo/Novo → Propostas/Novo.'
    ),
)
async def post_safra_calculation_new(
    body: CalculationInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> CalculationOutSchema:
    return await controller.post_calculo_novo(body)


@router.post(
    '/calculation/refin',
    response_model=CalculationOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Simulate consignado values (Refin)',
    description='Proxy para Calculo/Refin da API Safra.',
)
async def post_safra_calculation_refin(
    body: CalculationRefinInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> CalculationOutSchema:
    return await controller.post_calculo_refin(body)


@router.post(
    '/calculation/portability',
    response_model=CalculationOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Simulate consignado values (Portabilidade)',
    description='Proxy para Calculo/Portabilidade da API Safra.',
)
async def post_safra_calculation_portability(
    body: CalculationPortabilityInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> CalculationOutSchema:
    return await controller.post_calculo_portabilidade(body)


@router.post(
    '/calculation/portability-refin',
    response_model=CalculationPortRefinOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Simulate consignado values (Portabilidade + Refin)',
    description='Proxy para Calculo/PortabilidadeRefin da API Safra.',
)
async def post_safra_calculation_portability_refin(
    body: CalculationPortRefinInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> CalculationPortRefinOutSchema:
    return await controller.post_calculo_portabilidade_refin(body)


@router.get(
    '/tables/{convenio_id}',
    response_model=List[SafraTablesOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List safra tables',
    description='List safra tables from Safra',
)
async def get_safra_tables(
    convenio_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraTablesOutSchema]:
    return await controller.list_safra_tables(convenio_id)


@router.post(
    '/proposal',
    response_model=ProposalResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Post proposal',
    description='Post proposal from Safra',
)
async def post_safra_proposal(
    body: ProposalSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ProposalResponseSchema:
    return await controller.post_safra_proposal(body)


@router.post(
    '/proposals/{proposal_id}/attachments',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Attach document to proposal',
    description='Proxy para Propostas/{idProposta}/DocumentoAnexo da API Safra.',
)
async def post_safra_proposal_attachment(
    proposal_id: int,
    body: ProposalAttachmentInSchema,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.post_proposal_attachment(proposal_id, body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '/leads',
    response_model=List[LeadOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List Safra leads',
)
async def get_safra_leads(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[LeadOutSchema]:
    return await controller.list_leads()


@router.get(
    '/leads/download',
    status_code=status.HTTP_200_OK,
    summary='Download Safra leads CSV',
)
async def get_safra_leads_download(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    payload = await controller.download_leads_csv()
    return Response(
        content=payload,
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="safra-leads.csv"'},
    )


@router.post(
    '/leads/return-upload',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Upload lead return data (JSON)',
    description='Proxy para Lead/UploadRetorno da API Safra.',
)
async def post_safra_leads_return_upload(
    body: List[LeadReturnUploadItemInSchema],
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.upload_leads_return(body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    '/leads/return-upload/file',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Upload lead return file',
    description='Proxy para Lead/UploadArquivoRetorno da API Safra.',
)
async def post_safra_leads_return_upload_file(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    file: UploadFile = File(..., description='Arquivo de retorno de leads'),
) -> Response:
    content = await file.read()
    filename = file.filename or 'leads-retorno.csv'
    await controller.upload_leads_return_file(content, filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '/proposal/formalization-link',
    response_model=List[FormalizationLinkOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Get proposal formalization link',
    description='Proxy para Propostas/ObterLinkFormalizacao da API Safra.',
)
async def get_safra_proposal_formalization_link(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    id_proposta: Optional[int] = None,
    id_cliente: Optional[int] = None,
    dt_inicio: Optional[datetime] = None,
    dt_fim: Optional[datetime] = None,
    id_convenio: Optional[int] = None,
) -> List[FormalizationLinkOutSchema]:
    return await controller.get_proposal_formalization_link(
        id_proposta=id_proposta,
        id_cliente=id_cliente,
        dt_inicio=dt_inicio,
        dt_fim=dt_fim,
        id_convenio=id_convenio,
    )


@router.get(
    '/employing-bodies/{financial_agreement_id}',
    response_model=List[SafraEmployingBodySchema],
    status_code=status.HTTP_200_OK,
    summary='List employing bodies',
    description='List employing bodies from Safra',
)
async def get_safra_employing_bodies(
    financial_agreement_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraEmployingBodySchema]:
    return await controller.get_employing_bodies(financial_agreement_id)


@router.get(
    '/professions/{financial_agreement_id}',
    response_model=List[SafraProfessionsSchema],
    status_code=status.HTTP_200_OK,
    summary='List professions',
    description='List professions from Safra',
)
async def get_safra_professions(
    financial_agreement_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraProfessionsSchema]:
    return await controller.get_professions(financial_agreement_id)


@router.get(
    '/legal-regime/{financial_agreement_id}',
    response_model=List[SafraRegimeLegalSchema],
    status_code=status.HTTP_200_OK,
    summary='List legal regime',
    description='List legal regime from Safra',
)
async def get_safra_legal_regime(
    financial_agreement_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraRegimeLegalSchema]:
    return await controller.get_legal_regime(financial_agreement_id)


@router.get(
    '/employee-situation/{financial_agreement_id}/{legal_regime_id}',
    response_model=List[EmployeeSituationSchema],
    status_code=status.HTTP_200_OK,
    summary='List employee situation',
    description='List employee situation from Safra',
)
async def get_safra_employee_situation(
    financial_agreement_id: int,
    legal_regime_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[EmployeeSituationSchema]:
    return await controller.get_employee_situation(
        financial_agreement_id, legal_regime_id
    )


@router.get(
    '/financial-agreements/{convenio_id}/operational-guide',
    response_model=SafraOperationalGuideOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Operational guide for convenio',
)
async def get_safra_operational_guide(
    convenio_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> SafraOperationalGuideOutSchema:
    return await controller.get_operational_guide(convenio_id)


@router.get(
    '/tables/{table_id}/bands',
    response_model=List[SafraInterestTableBandOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List interest table bands',
)
async def get_safra_interest_table_bands(
    table_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraInterestTableBandOutSchema]:
    return await controller.list_interest_table_bands(table_id)


@router.get(
    '/catalog/agencies',
    response_model=List[SafraAgencyOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List Safra agencies',
)
async def get_safra_agencies(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraAgencyOutSchema]:
    return await controller.list_agencies()


@router.get(
    '/catalog/positions/{profession_id}',
    response_model=List[SafraPositionOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List positions for profession',
)
async def get_safra_positions(
    profession_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraPositionOutSchema]:
    return await controller.list_positions(profession_id)


@router.get(
    '/catalog/employment-bonds/{convenio_id}',
    response_model=List[SafraEmploymentBondOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List employment bonds',
)
async def get_safra_employment_bonds(
    convenio_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[SafraEmploymentBondOutSchema]:
    return await controller.list_employment_bonds(convenio_id)


@router.get(
    '/proposals/search',
    response_model=List[ProposalListItemOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Search proposals (Safra GET /Propostas)',
)
async def get_safra_proposals_search(
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    id_proposta: Optional[int] = None,
    id_cliente: Optional[int] = None,
    dt_inicio: Optional[datetime] = None,
    dt_fim: Optional[datetime] = None,
    id_convenio: Optional[int] = None,
    id_situacao: Optional[int] = None,
    id_tp_produto: Optional[int] = None,
) -> List[ProposalListItemOutSchema]:
    return await controller.list_proposals(
        id_proposta=id_proposta,
        id_cliente=id_cliente,
        dt_inicio=dt_inicio,
        dt_fim=dt_fim,
        id_convenio=id_convenio,
        id_situacao=id_situacao,
        id_tp_produto=id_tp_produto,
    )


@router.get(
    '/proposals/{proposal_id}/flow',
    response_model=List[ProposalFlowStepOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Proposal flow steps (FluxoProposta)',
)
async def get_safra_proposal_flow(
    proposal_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ProposalFlowStepOutSchema]:
    return await controller.get_proposal_flow(proposal_id)


@router.get(
    '/proposals/{proposal_id}/formalization-tracking',
    response_model=List[FormalizationTrackingOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Formalization tracking (AcompanhamentoFormalizacao)',
)
async def get_safra_formalization_tracking(
    proposal_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[FormalizationTrackingOutSchema]:
    return await controller.get_formalization_tracking(proposal_id)


@router.post(
    '/paradinha/{proposal_id}/approve',
    response_model=ParadinhaOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Approve paradinha (stop release)',
)
async def post_safra_paradinha_approve(
    proposal_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ParadinhaOutSchema:
    return await controller.approve_paradinha(proposal_id)


@router.post(
    '/paradinha/{proposal_id}/cancel',
    response_model=ParadinhaOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Cancel paradinha proposal',
)
async def post_safra_paradinha_cancel(
    proposal_id: int,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ParadinhaOutSchema:
    return await controller.cancel_paradinha(proposal_id)


@router.get(
    '/contracts/registration-data/cpf/{cpf}',
    response_model=List[ContractRegistrationDataOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract registration data by CPF',
)
async def get_safra_contracts_registration_by_cpf(
    cpf: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractRegistrationDataOutSchema]:
    return await controller.get_contracts_registration_by_cpf(cpf)


@router.get(
    '/contracts/registration-data/date/{proposal_date}',
    response_model=List[ContractRegistrationDataOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract registration data by proposal date',
)
async def get_safra_contracts_registration_by_date(
    proposal_date: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractRegistrationDataOutSchema]:
    return await controller.get_contracts_registration_by_date(proposal_date)


@router.get(
    '/contracts/registration-data/proposal/{proposal_number}',
    response_model=List[ContractRegistrationDataOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract registration data by proposal number',
)
async def get_safra_contracts_registration_by_proposal(
    proposal_number: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractRegistrationDataOutSchema]:
    return await controller.get_contracts_registration_by_proposal(proposal_number)


@router.get(
    '/contracts/loan/cpf/{cpf}',
    response_model=List[ContractLoanOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract loan data by CPF',
)
async def get_safra_contracts_loan_by_cpf(
    cpf: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractLoanOutSchema]:
    return await controller.get_contracts_loan_by_cpf(cpf)


@router.get(
    '/contracts/loan/date/{proposal_date}',
    response_model=List[ContractLoanOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract loan data by proposal date',
)
async def get_safra_contracts_loan_by_date(
    proposal_date: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractLoanOutSchema]:
    return await controller.get_contracts_loan_by_date(proposal_date)


@router.get(
    '/contracts/loan/proposal/{proposal_number}',
    response_model=List[ContractLoanOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract loan data by proposal number',
)
async def get_safra_contracts_loan_by_proposal(
    proposal_number: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractLoanOutSchema]:
    return await controller.get_contracts_loan_by_proposal(proposal_number)


@router.get(
    '/contracts/financial/cpf/{cpf}',
    response_model=List[ContractFinancialOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract financial data by CPF',
)
async def get_safra_contracts_financial_by_cpf(
    cpf: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractFinancialOutSchema]:
    return await controller.get_contracts_financial_by_cpf(cpf)


@router.get(
    '/contracts/financial/date/{proposal_date}',
    response_model=List[ContractFinancialOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract financial data by proposal date',
)
async def get_safra_contracts_financial_by_date(
    proposal_date: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractFinancialOutSchema]:
    return await controller.get_contracts_financial_by_date(proposal_date)


@router.get(
    '/contracts/financial/proposal/{proposal_number}',
    response_model=List[ContractFinancialOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract financial data by proposal number',
)
async def get_safra_contracts_financial_by_proposal(
    proposal_number: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractFinancialOutSchema]:
    return await controller.get_contracts_financial_by_proposal(proposal_number)


@router.get(
    '/contracts/status/cpf/{cpf}',
    response_model=List[ContractStatusOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract status by CPF',
)
async def get_safra_contracts_status_by_cpf(
    cpf: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractStatusOutSchema]:
    return await controller.get_contracts_status_by_cpf(cpf)


@router.get(
    '/contracts/status/date/{proposal_date}',
    response_model=List[ContractStatusOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract status by proposal date',
)
async def get_safra_contracts_status_by_date(
    proposal_date: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractStatusOutSchema]:
    return await controller.get_contracts_status_by_date(proposal_date)


@router.get(
    '/contracts/status/proposal/{proposal_number}',
    response_model=List[ContractStatusOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Contract status by proposal number',
)
async def get_safra_contracts_status_by_proposal(
    proposal_number: str,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ContractStatusOutSchema]:
    return await controller.get_contracts_status_by_proposal(proposal_number)
