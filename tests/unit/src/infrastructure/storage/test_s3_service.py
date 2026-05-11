import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import src.infrastructure.storage.s3_service as s3_service_mod
from src.infrastructure.storage.s3_client import UploadResult

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clear_s3_service_cache() -> None:
    s3_service_mod.get_s3_storage.cache_clear()
    yield
    s3_service_mod.get_s3_storage.cache_clear()


def test_get_s3_storage_singleton() -> None:
    fake = MagicMock()
    with patch.object(s3_service_mod.S3Storage, 'from_settings') as mock_from_settings:
        mock_from_settings.return_value = fake
        first = s3_service_mod.get_s3_storage()
        second = s3_service_mod.get_s3_storage()
    assert first is second is fake
    mock_from_settings.assert_called_once()


@pytest.mark.asyncio
async def test_upload_proposal_document_files() -> None:
    sid = uuid.uuid4()
    storage = MagicMock()
    storage.upload_proposal_documents = AsyncMock(
        return_value=[
            UploadResult(
                url='u',
                key='k',
                content_type='image/jpeg',
                size_bytes=1,
            ),
        ],
    )
    files = [MagicMock()]

    with patch.object(s3_service_mod, 'get_s3_storage', return_value=storage):
        out = await s3_service_mod.upload_proposal_document_files(
            files=files,
            scope_id=sid,
        )

    assert len(out) == 1
    assert out[0].key == 'k'
    storage.upload_proposal_documents.assert_awaited_once_with(
        files=files,
        scope_id=sid,
    )
