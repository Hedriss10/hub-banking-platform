from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import src.interface.api.v2.routes.proposal as proposal_routes_mod
from fastapi import HTTPException
from httpx import AsyncClient
from src.domain.dtos.proposal import ProposalAggregateOutDTO, ProposalOutDTO
from src.infrastructure.storage.s3_client import UploadResult
from src.interface.api.v2.routes.proposal import upload_proposal_documents
from starlette import status

pytestmark = pytest.mark.unit

_PROPOSALS = '/api/v2/proposals'


def _aggregate_out(eid):
    fid = uuid4()
    pid = uuid4()
    now = datetime.now(timezone.utc)
    return ProposalAggregateOutDTO(
        proposal=ProposalOutDTO(
            name='Cliente',
            financial_agreements_id=fid,
            cpf='12345678901234',
            place_of_birth='BR',
            created_by=eid,
            id=pid,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        ),
        account=None,
        documents=[],
        loans=[],
    )


@pytest.mark.asyncio
async def test_post_create_proposal(
    async_proposal_client: AsyncClient,
    mock_proposal_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    out = _aggregate_out(eid)
    mock_proposal_use_case.create_proposal_with_relations = AsyncMock(return_value=out)

    fa = str(out.proposal.financial_agreements_id)
    response = await async_proposal_client.post(
        _PROPOSALS,
        json={
            'proposal': {
                'name': 'Cliente',
                'financial_agreements_id': fa,
                'cpf': '12345678901234',
                'place_of_birth': 'BR',
            },
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body['proposal']['id'] == str(out.proposal.id)
    mock_proposal_use_case.create_proposal_with_relations.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_proposals(
    async_proposal_client: AsyncClient,
    mock_proposal_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    out = _aggregate_out(eid)
    mock_proposal_use_case.list_proposals = AsyncMock(return_value=[out.proposal])

    response = await async_proposal_client.get(_PROPOSALS)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == str(out.proposal.id)


@pytest.mark.asyncio
async def test_get_proposal_by_id(
    async_proposal_client: AsyncClient,
    mock_proposal_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    out = _aggregate_out(eid)
    mock_proposal_use_case.get_proposal_aggregate = AsyncMock(return_value=out)

    pid = out.proposal.id
    response = await async_proposal_client.get(f'{_PROPOSALS}/{pid}')
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body['proposal']['id'] == str(pid)


@pytest.mark.asyncio
async def test_patch_update_proposal(
    async_proposal_client: AsyncClient,
    mock_proposal_use_case: AsyncMock,
) -> None:
    eid = uuid4()
    out = _aggregate_out(eid)
    mock_proposal_use_case.update_proposal = AsyncMock(return_value=out)

    pid = out.proposal.id
    response = await async_proposal_client.patch(
        f'{_PROPOSALS}/{pid}',
        json={'name': 'Cliente atualizado'},
    )
    assert response.status_code == status.HTTP_200_OK
    mock_proposal_use_case.update_proposal.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_proposal(
    async_proposal_client: AsyncClient,
    mock_proposal_use_case: AsyncMock,
) -> None:
    mock_proposal_use_case.delete_proposal = AsyncMock(return_value=None)
    pid = uuid4()
    response = await async_proposal_client.delete(f'{_PROPOSALS}/{pid}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_proposal_use_case.delete_proposal.assert_awaited_once_with(pid)


@pytest.mark.asyncio
async def test_post_upload_proposal_documents_success(
    async_proposal_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_upload(*, files, scope_id):
        _ = scope_id
        assert len(files) == 1
        return [
            UploadResult(
                url='https://u',
                key='k/j',
                content_type='image/jpeg',
                size_bytes=4,
            ),
        ]

    monkeypatch.setattr(
        proposal_routes_mod,
        'upload_proposal_document_files',
        fake_upload,
    )
    files = [('files', ('a.jpg', b'data', 'image/jpeg'))]
    response = await async_proposal_client.post(
        f'{_PROPOSALS}/documents/upload',
        files=files,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['key'] == 'k/j'


@pytest.mark.asyncio
async def test_upload_route_raises_when_all_files_have_no_filename(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def boom(*, files, scope_id):
        raise AssertionError('should not run')

    monkeypatch.setattr(
        'src.interface.api.v2.routes.proposal.upload_proposal_document_files',
        boom,
    )

    f = MagicMock()
    f.filename = None
    with pytest.raises(HTTPException) as exc_info:
        await upload_proposal_documents(files=[f], _employee_id=uuid4())
    assert exc_info.value.detail == 'Send at least one file'
