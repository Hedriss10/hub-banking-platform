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
    summary='Obter token Safra',
    description=('Requires header Authorization: Bearer with the access_token'),
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
        'Requires Authorization: Bearer (JWT of the employee). '
        'The Safra API token is obtained on the server using'
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
        'Margin consultation via Safra ConsultaMargem/Bpo. '
        'Requires Authorization: Bearer (employee JWT); '
        'Safra token is obtained server-side. '
        'Envie `cpf` como string para preservar zeros à esquerda.'
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
    summary='Lista batch_job_id distintos (Postgres)',
    description=(
        'Retorna todos os identifiers de jobs com ao menos uma linha persistida '
        'em safra_batch_search (não inclui registros marcados como deletados).'
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
    summary='Upload CSV — batch consulta margem Safra',
    description=(
        'Recebe CSV UTF-8 com cabeçalho (convenio, idProduto, cpf, matricula; '
        'telefones opcionais phone_one … phone_five). '
        'O processamento roda em segundo plano; use GET /batch/search/{job_id}/status. '
        'Requer REDIS_URL configurado.'
    ),
)
async def post_safra_batch_search_upload(
    background_tasks: BackgroundTasks,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    file: UploadFile = File(..., description='Arquivo CSV UTF-8'),
) -> SafraBatchUploadOutSchema:
    return await controller.upload_batch_search_csv(file, background_tasks)


@router.get(
    '/batch/search/{job_id}/status',
    response_model=SafraBatchJobStatusOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Status do job de batch Safra',
    description=(
        'Polling pelo frontend; estado fica em Redis até expirar (TTL configurável).'
    ),
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
    summary='Export CSV dos resultados do lote',
    description=(
        'CSV UTF-8 (BOM) com delimitador `;`, mesmos resultados gravados pelo worker '
        '(batch_job_id igual ao job_id retornado no upload).'
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
    summary='Remove fisicamente o lote (Postgres)',
    description=(
        'Executa `DELETE` nas linhas de `safra_batch_search` com o `batch_job_id` '
        'informado (exclusão permanente — não usa `is_deleted`). '
        'Não altera dados no Redis; **404** se não houver linhas para esse UUID.'
    ),
)
async def delete_safra_batch_search_job(
    batch_job_id: UUID,
    controller: SafraControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.delete_batch_job_search_records(batch_job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
