from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from src.domain.dtos.safra import BankerResponse, MargemBpoOutputDto, TokenResponse
from starlette import status

pytestmark = pytest.mark.unit

_SAFRA_TOKEN = '/api/v2/safra/token'
_SAFRA_BANKS = '/api/v2/safra/banks'
_SAFRA_MARGIN_BPO = '/api/v2/safra/margin/bpo'
_SAFRA_BATCH_UPLOAD = '/api/v2/safra/batch/search/upload'
_SAFRA_BATCH_STATUS_TEMPLATE = '/api/v2/safra/batch/search/{job_id}/status'


_MARGEM_OUT = MargemBpoOutputDto(
    cpf='01437872506',
    margem=250.5,
    lotacao='L',
    autorizada=True,
    nome='N',
    secretaria='S',
    tipoServidor='T',
    cargo='C',
    regimeJuridico='R',
    dataAdmissao='2020-01-01',
    uf='SP',
    renda=5000.0,
    mensagemErro='',
    dataHoraConsulta='2026-01-01T00:00:00',
)


@pytest.mark.asyncio
async def test_post_safra_token(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.get_token = AsyncMock(
        return_value=TokenResponse.model_validate({'token': 'safra-jwt'})
    )
    response = await async_safra_client.post(_SAFRA_TOKEN)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['token'] == 'safra-jwt'
    mock_safra_use_case.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_safra_banks(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    row = BankerResponse(
        codigoBanco=1,
        nomeBanco='Bank',
        cnpj=12345678000190,
        ispb=12345678,
    )
    mock_safra_use_case.get_bankers = AsyncMock(return_value=[row])
    response = await async_safra_client.get(_SAFRA_BANKS)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['nomeBanco'] == 'Bank'
    mock_safra_use_case.get_bankers.assert_awaited_once()


@pytest.mark.asyncio
async def test_post_safra_margin_bpo(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    mock_safra_use_case.get_margem_bpo = AsyncMock(return_value=_MARGEM_OUT)
    payload = {
        'convenio': 1,
        'cpf': '01437872506',
        'idProduto': 2,
        'matricula': 'M-01',
    }
    response = await async_safra_client.post(_SAFRA_MARGIN_BPO, json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['margem'] == _MARGEM_OUT.margem
    assert data['cpf'] == '01437872506'
    mock_safra_use_case.get_margem_bpo.assert_awaited_once()
    dto_passed = mock_safra_use_case.get_margem_bpo.await_args.args[0]
    assert dto_passed.cpf == '01437872506'


@pytest.mark.asyncio
async def test_post_safra_batch_upload_requires_redis(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(REDIS_URL=None),
    )
    csv_body = 'convenio,idProduto,cpf,matricula\n10237,1,38585766034,303048269980000\n'
    files = {'file': ('lote.csv', csv_body.encode('utf-8'), 'text/csv')}
    response = await async_safra_client.post(_SAFRA_BATCH_UPLOAD, files=files)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_post_safra_batch_upload_accepted(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(
            REDIS_URL='redis://localhost',
            SAFRA_BATCH_JOB_TTL_SECONDS=3600,
        ),
    )
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.job_save',
        AsyncMock(),
    )
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.run_safra_batch_job',
        AsyncMock(),
    )
    csv_body = 'convenio,idProduto,cpf,matricula\n10237,1,01437872506,303048269980000\n'
    files = {'file': ('lote.csv', csv_body.encode('utf-8'), 'text/csv')}
    response = await async_safra_client.post(_SAFRA_BATCH_UPLOAD, files=files)
    assert response.status_code == status.HTTP_202_ACCEPTED
    body = response.json()
    assert body['status'] == 'queued'
    assert body['total_rows'] == 1


@pytest.mark.asyncio
async def test_post_safra_batch_upload_csv_invalido(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(REDIS_URL='redis://localhost'),
    )
    csv_body = 'convenio,idProduto,cpf,matricula\n'
    files = {'file': ('vazio.csv', csv_body.encode('utf-8'), 'text/csv')}
    response = await async_safra_client.post(_SAFRA_BATCH_UPLOAD, files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'messages' in response.json()['detail']


@pytest.mark.asyncio
async def test_get_safra_batch_status(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    generate_uuid,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(REDIS_URL='redis://localhost'),
    )
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.job_get',
        AsyncMock(
            return_value={
                'status': 'completed',
                'total_rows': 2,
                'processed_rows': 2,
                'failed_rows': 0,
                'detail': None,
            },
        ),
    )
    jid = generate_uuid
    url = _SAFRA_BATCH_STATUS_TEMPLATE.format(job_id=jid)
    response = await async_safra_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'completed'


@pytest.mark.asyncio
async def test_get_safra_batch_status_sem_redis(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    generate_uuid,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(REDIS_URL=None),
    )
    url = _SAFRA_BATCH_STATUS_TEMPLATE.format(job_id=generate_uuid)
    response = await async_safra_client.get(url)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_get_safra_batch_status_job_ausente(
    async_safra_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    generate_uuid,
) -> None:
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.get_settings',
        lambda: MagicMock(REDIS_URL='redis://localhost'),
    )
    monkeypatch.setattr(
        'src.interface.api.v2.controller.safra.job_get',
        AsyncMock(return_value=None),
    )
    url = _SAFRA_BATCH_STATUS_TEMPLATE.format(job_id=generate_uuid)
    response = await async_safra_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
