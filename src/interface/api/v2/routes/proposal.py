from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

from src.infrastructure.storage.s3_service import upload_proposal_document_files
from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.proposal import ProposalControllerDep
from src.interface.api.v2.schemas.proposal import (
    ProposalCreateSchema,
    ProposalDocumentsUploadOutSchema,
    ProposalDocumentUploadItemSchema,
    ProposalOutSchema,
    ProposalRecordOutSchema,
    ProposalUpdateSchema,
)

tags_metadata = {
    'name': 'Proposals',
    'description': 'Proposals module.',
}

router = APIRouter(
    prefix='/proposals',
    tags=[tags_metadata['name']],
)


@router.post(
    '/documents/upload',
    response_model=ProposalDocumentsUploadOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Upload of documents (Contabo/S3)',
    description=(
        'Send multiple files (images or PDF). Returns URL and key to use in '
        '`documents[].document_path` when creating the proposal.'
    ),
)
async def upload_proposal_documents(
    files: Annotated[
        list[UploadFile],
        File(
            description=(
                'Images or PDF; types in S3_ALLOWED_PROPOSAL_CONTENT_TYPES (.env)'
            ),
        ),
    ],
    _employee_id: CurrentEmployeeIdDep,
) -> ProposalDocumentsUploadOutSchema:
    uploads = [f for f in files if f.filename]
    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Send at least one file',
        )
    results = await upload_proposal_document_files(files=uploads, scope_id=_employee_id)
    return ProposalDocumentsUploadOutSchema(
        items=[
            ProposalDocumentUploadItemSchema(
                url=r.url,
                key=r.key,
                content_type=r.content_type,
                size_bytes=r.size_bytes,
            )
            for r in results
        ]
    )


@router.get(
    '',
    response_model=List[ProposalRecordOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List proposals',
    description=(
        'Lists non-deleted proposals (proposal row only); ordered by `updated_at` desc.'
    ),
)
async def list_proposals(
    controller: ProposalControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[ProposalRecordOutSchema]:
    _ = _employee_id
    return await controller.list_proposals()


@router.post(
    '',
    response_model=ProposalOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create proposal',
    description=(
        'Created proposal in cascade (account, documents, loans). '
        'For attachments, send first `POST .../documents/upload` and use '
        '`url` or `key` returned in `documents[].document_path`.'
    ),
)
async def create_proposal(
    proposal: ProposalCreateSchema,
    controller: ProposalControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ProposalOutSchema:
    return await controller.create_proposal(proposal, _employee_id)


@router.get(
    '/{proposal_id}',
    response_model=ProposalOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Get proposal by id',
    description=(
        'Returns proposal with account, uploaded documents references, and loans '
        '(non-deleted children).'
    ),
)
async def get_proposal(
    proposal_id: UUID,
    controller: ProposalControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ProposalOutSchema:
    _ = _employee_id
    return await controller.get_proposal(proposal_id)


@router.patch(
    '/{proposal_id}',
    response_model=ProposalOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Update proposal',
    description=(
        'Partial update of the proposal entity only (not account, documents, or loans).'
    ),
)
async def update_proposal(
    proposal_id: UUID,
    patch: ProposalUpdateSchema,
    controller: ProposalControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> ProposalOutSchema:
    _ = _employee_id
    return await controller.update_proposal(proposal_id, patch)


@router.delete(
    '/{proposal_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete proposal',
    description='Soft-deletes the proposal row (`is_deleted=true`).',
)
async def delete_proposal(
    proposal_id: UUID,
    controller: ProposalControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    _ = _employee_id
    await controller.delete_proposal(proposal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
