from datetime import timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.domain.dtos.safra import MargemBpoOutputDto, SafraBatchSearchDto
from src.infrastructure.workers.processing_batch_safra import (
    _parse_iso_datetime,
    run_safra_batch_job,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def margem_payload_ok() -> MargemBpoOutputDto:
    return MargemBpoOutputDto(
        cpf='01437872506',
        margem=10.0,
        lotacao='L',
        autorizada=True,
        nome='N',
        secretaria='S',
        tipoServidor='T',
        cargo='C',
        regimeJuridico='R',
        dataAdmissao='2020-01-01T00:00:00Z',
        uf='SP',
        renda=1.0,
        mensagemErro='',
        dataHoraConsulta='2026-01-01T00:00:00',
    )


@pytest.mark.asyncio
async def test_run_batch_payload_invalido_grava_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_save = AsyncMock()
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_save',
        job_save,
    )

    jid = uuid4()
    await run_safra_batch_job(jid, [{'cpf': 'x'}])

    job_save.assert_awaited()
    last = job_save.await_args_list[-1][0][1]
    assert last['status'] == 'failed'


@pytest.mark.asyncio
async def test_run_batch_linha_ok_insere_sessao(
    monkeypatch: pytest.MonkeyPatch,
    margem_payload_ok: MargemBpoOutputDto,
) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock(return_value=cm)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.get_session_factory',
        lambda: factory,
    )
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_save',
        AsyncMock(),
    )
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_get',
        AsyncMock(return_value={'status': 'queued'}),
    )

    repo_instance = MagicMock()
    repo_instance.get_margem_bpo = AsyncMock(return_value=margem_payload_ok)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.SafraExternalRepository',
        lambda: repo_instance,
    )

    row = SafraBatchSearchDto(
        convenio=1,
        idProduto=1,
        cpf='01437872506',
        matricula='M',
    )

    jid = uuid4()
    await run_safra_batch_job(jid, [row.model_dump(mode='json')])

    session.add.assert_called_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_batch_linha_erro_api_insere_sem_margem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock(return_value=cm)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.get_session_factory',
        lambda: factory,
    )
    job_save = AsyncMock()
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_save',
        job_save,
    )
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_get',
        AsyncMock(return_value={'status': 'queued'}),
    )

    repo_instance = MagicMock()
    repo_instance.get_margem_bpo = AsyncMock(side_effect=RuntimeError('upstream'))

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.SafraExternalRepository',
        lambda: repo_instance,
    )

    row = SafraBatchSearchDto(
        convenio=1,
        idProduto=1,
        cpf='01437872506',
        matricula='M',
    )

    jid = uuid4()
    await run_safra_batch_job(jid, [row.model_dump(mode='json')])

    session.add.assert_called_once()
    args_model = session.add.call_args.args[0]
    assert args_model.margem is None

    completed = job_save.await_args_list[-1][0][1]
    assert completed['status'] == 'completed'
    assert completed['failed_rows'] == 1


@pytest.mark.asyncio
async def test_parse_iso_datetime_invalido_via_worker() -> None:
    assert _parse_iso_datetime('não-iso') is None


@pytest.mark.asyncio
async def test_parse_iso_datetime_none_vazio_e_naive() -> None:
    assert _parse_iso_datetime(None) is None
    assert _parse_iso_datetime('') is None
    assert _parse_iso_datetime('   ') is None

    dt = _parse_iso_datetime('2020-05-10T08:15:30')
    assert dt is not None
    assert dt.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_run_batch_commit_falha_marca_abortado(
    monkeypatch: pytest.MonkeyPatch,
    margem_payload_ok: MargemBpoOutputDto,
) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock(side_effect=RuntimeError('commit'))

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock(return_value=cm)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.get_session_factory',
        lambda: factory,
    )
    job_save = AsyncMock()
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_save',
        job_save,
    )
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_get',
        AsyncMock(return_value=None),
    )

    repo_instance = MagicMock()
    repo_instance.get_margem_bpo = AsyncMock(return_value=margem_payload_ok)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.SafraExternalRepository',
        lambda: repo_instance,
    )

    row = SafraBatchSearchDto(
        convenio=1,
        idProduto=1,
        cpf='01437872506',
        matricula='M',
    )

    jid = uuid4()
    await run_safra_batch_job(jid, [row.model_dump(mode='json')])

    aborted = job_save.await_args_list[-1][0][1]
    assert aborted['status'] == 'failed'
    assert 'commit' in aborted['detail']


@pytest.mark.asyncio
async def test_run_batch_merge_campos_existentes_do_redis(
    monkeypatch: pytest.MonkeyPatch,
    margem_payload_ok: MargemBpoOutputDto,
) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock(return_value=cm)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.get_session_factory',
        lambda: factory,
    )
    job_save = AsyncMock()
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_save',
        job_save,
    )
    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.job_get',
        AsyncMock(return_value={'rastreio': 'abc'}),
    )

    repo_instance = MagicMock()
    repo_instance.get_margem_bpo = AsyncMock(return_value=margem_payload_ok)

    monkeypatch.setattr(
        'src.infrastructure.workers.processing_batch_safra.SafraExternalRepository',
        lambda: repo_instance,
    )

    row = SafraBatchSearchDto(
        convenio=1,
        idProduto=1,
        cpf='01437872506',
        matricula='M',
    )

    jid = uuid4()
    await run_safra_batch_job(jid, [row.model_dump(mode='json')])

    primeiro = job_save.await_args_list[0][0][1]
    assert primeiro['rastreio'] == 'abc'
