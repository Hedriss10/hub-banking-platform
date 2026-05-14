from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
import src.infrastructure.repositories.safra_batch_search_postgres as smb_module
from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.infrastructure.repositories.safra_batch_search_postgres import (
    SafraBatchSearchPostgresRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(mock_session: AsyncMock) -> SafraBatchSearchPostgresRepository:
    return SafraBatchSearchPostgresRepository(mock_session)


def _mock_scalars_all(rows: list) -> MagicMock:
    scal = MagicMock()
    scal.all = MagicMock(return_value=rows)
    out = MagicMock()
    out.scalars = MagicMock(return_value=scal)
    return out


@pytest.mark.asyncio
async def test_list_distinct_batch_job_ids(
    repository: SafraBatchSearchPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    mock_session.execute = AsyncMock(return_value=_mock_scalars_all([jid]))
    out = await repository.list_distinct_batch_job_ids()
    assert list(out) == [jid]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_rows_for_batch_job(
    repository: SafraBatchSearchPostgresRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    model_row = MagicMock()
    dto = SafraBatchSearchExportRowDTO(batch_job_id=jid)

    monkeypatch.setattr(
        smb_module.SafraBatchSearchExportRowDTO,
        'model_validate',
        classmethod(lambda _cls, _m: dto),
    )
    mock_session.execute = AsyncMock(return_value=_mock_scalars_all([model_row]))

    out = await repository.list_rows_for_batch_job(jid)
    assert list(out) == [dto]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_rows_for_batch_job_returns_count(
    repository: SafraBatchSearchPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    exec_result = MagicMock()
    exec_result.rowcount = 4
    mock_session.execute = AsyncMock(return_value=exec_result)
    mock_session.commit = AsyncMock()

    expected_deleted = 4
    deleted = await repository.delete_rows_for_batch_job(jid)

    assert deleted == expected_deleted
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_rows_for_batch_job_rowcount_none(
    repository: SafraBatchSearchPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    exec_result = MagicMock()
    exec_result.rowcount = None
    mock_session.execute = AsyncMock(return_value=exec_result)
    mock_session.commit = AsyncMock()

    deleted = await repository.delete_rows_for_batch_job(jid)

    assert deleted == 0
    mock_session.commit.assert_awaited_once()
