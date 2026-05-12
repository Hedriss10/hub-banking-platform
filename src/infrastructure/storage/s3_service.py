from __future__ import annotations

from functools import lru_cache
from uuid import UUID

from fastapi import UploadFile

from src.infrastructure.storage.s3_client import S3Storage, UploadResult


@lru_cache()
def get_s3_storage() -> S3Storage:
    return S3Storage.from_settings()


async def upload_proposal_document_files(
    *, files: list[UploadFile], scope_id: UUID
) -> list[UploadResult]:
    """
    Envia vários arquivos ao bucket (Contabo/S3 compatível) sob
    `proposals/staging/{scope_id}/documents/`.

    O `scope_id` costuma ser o `employee_id` do JWT para isolar uploads
    por operador até a proposta existir; após criar a proposta, o frontend
    envia em `documents[].document_path` a `url` ou `key` retornada aqui.
    """
    storage = get_s3_storage()
    return await storage.upload_proposal_documents(files=files, scope_id=scope_id)
