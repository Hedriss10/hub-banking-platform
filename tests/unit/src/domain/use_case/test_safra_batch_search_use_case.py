from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.domain.exceptions.safra_batch_search import SafraBatchSearchNotFoundException
from src.domain.use_case.safra_batch_search import SafraBatchSearchUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_distinct_batch_job_ids_passes_through() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    repository = AsyncMock()
    repository.list_distinct_batch_job_ids = AsyncMock(return_value=[jid])
    uc = SafraBatchSearchUseCase(repository)
    out = await uc.list_distinct_batch_job_ids()
    assert list(out) == [jid]
    repository.list_distinct_batch_job_ids.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_rows_for_export_returns_rows() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    row = SafraBatchSearchExportRowDTO(batch_job_id=jid)
    repository = AsyncMock()
    repository.list_rows_for_batch_job = AsyncMock(return_value=[row])
    uc = SafraBatchSearchUseCase(repository)
    out = await uc.list_rows_for_export(jid)
    assert list(out) == [row]
    repository.list_rows_for_batch_job.assert_awaited_once_with(jid)


@pytest.mark.asyncio
async def test_list_rows_for_export_raises_when_empty() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    repository = AsyncMock()
    repository.list_rows_for_batch_job = AsyncMock(return_value=[])
    uc = SafraBatchSearchUseCase(repository)
    with pytest.raises(SafraBatchSearchNotFoundException):
        await uc.list_rows_for_export(jid)


@pytest.mark.asyncio
async def test_delete_persisted_batch_job_rows_success() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    repository = AsyncMock()
    repository.delete_rows_for_batch_job = AsyncMock(return_value=2)
    uc = SafraBatchSearchUseCase(repository)
    await uc.delete_persisted_batch_job_rows(jid)
    repository.delete_rows_for_batch_job.assert_awaited_once_with(jid)


@pytest.mark.asyncio
async def test_delete_persisted_batch_job_rows_raises_when_zero_deleted() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    repository = AsyncMock()
    repository.delete_rows_for_batch_job = AsyncMock(return_value=0)
    uc = SafraBatchSearchUseCase(repository)
    with pytest.raises(SafraBatchSearchNotFoundException):
        await uc.delete_persisted_batch_job_rows(jid)
