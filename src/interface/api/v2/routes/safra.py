from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, Response, UploadFile, status

from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.safra import SafraControllerDep
from src.interface.api.v2.schemas.safra import (
    BankerOutSchema,
    MargemBpoInSchema,
    MargemBpoOutSchema,
    SafraBatchJobIdsOutSchema,
    SafraBatchJobStatusOutSchema,
    SafraBatchUploadOutSchema,
    TokenOutSchema,
)
from src.interface.api.v2.schemas.safra_credit_ligth_house import (
    CreditLighthouseInSchema,
    CreditLighthouseOutSchema,
)
from src.interface.api.v2.schemas.safra_financial_agreements import (
    FinancialAgreementOutSchema,
)
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
