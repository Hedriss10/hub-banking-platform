from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.infrastructure.storage.s3_service import upload_proposal_document_files
from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.proposal import ProposalControllerDep
from src.interface.api.v2.schemas.proposal import (
    ProposalCreateSchema,
    ProposalDocumentsUploadOutSchema,
    ProposalDocumentUploadItemSchema,
    ProposalOutSchema,
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
