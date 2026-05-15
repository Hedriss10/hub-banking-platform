from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from src.domain.dtos.safra import BankerResponse, MargemBpoOutputDto, TokenResponse
from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.exceptions.safra_batch_search import SafraBatchSearchNotFoundException
from starlette import status
from tests.fixtures.safra_test_constants import SAFRA_TEST_CNPJ

pytestmark = pytest.mark.unit

_SAFRA_TOKEN = '/api/v2/safra/token'
_SAFRA_BANKS = '/api/v2/safra/banks'
_SAFRA_MARGIN_BPO = '/api/v2/safra/margin/bpo'
_SAFRA_BATCH_UPLOAD = '/api/v2/safra/batch/search/upload'
_SAFRA_BATCH_STATUS_TEMPLATE = '/api/v2/safra/batch/search/{job_id}/status'
_SAFRA_BATCH_JOB_IDS = '/api/v2/safra/batch/search/job-ids'
_SAFRA_BATCH_EXPORT_TEMPLATE = '/api/v2/safra/batch/search/{job_id}/export'
_SAFRA_BATCH_DELETE_TEMPLATE = '/api/v2/safra/batch/search/{job_id}'
_SAFRA_FINANCIAL_AGREEMENTS = '/api/v2/safra/financial-agreements'


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
        cnpj=SAFRA_TEST_CNPJ,
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


@pytest.mark.asyncio
async def test_get_safra_batch_job_ids(
    async_safra_client: AsyncClient,
    mock_safra_batch_search_use_case: AsyncMock,
    generate_uuid,
) -> None:
    jid = generate_uuid
    mock_safra_batch_search_use_case.list_distinct_batch_job_ids = AsyncMock(
        return_value=[jid],
    )
    response = await async_safra_client.get(_SAFRA_BATCH_JOB_IDS)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['batch_job_ids'] == [str(jid)]
    mock_safra_batch_search_use_case.list_distinct_batch_job_ids.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_safra_batch_export_csv(
    async_safra_client: AsyncClient,
    mock_safra_batch_search_use_case: AsyncMock,
    generate_uuid,
) -> None:
    jid = generate_uuid
    row = SafraBatchSearchExportRowDTO(
        batch_job_id=jid,
        cpf='01437872506',
        margem=2.0,
        lotacao='L',
        autorizada=False,
        nome='N',
        secretaria='S',
        tipoServidor='T',
        cargo=None,
        regimeJuridico=None,
        dataAdmissao=None,
        uf='RJ',
        renda=None,
        phone_one=None,
        phone_two=None,
        phone_three=None,
        phone_four=None,
        phone_five=None,
    )
    mock_safra_batch_search_use_case.list_rows_for_export = AsyncMock(
        return_value=[row],
    )
    url = _SAFRA_BATCH_EXPORT_TEMPLATE.format(job_id=jid)
    response = await async_safra_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'text/csv' in response.headers.get('content-type', '')
    assert 'attachment' in response.headers.get('content-disposition', '').lower()
    text = response.content.decode('utf-8-sig')
    assert text.split('\r\n')[0].startswith('batch_job_id')
    assert ';false;' in text
    mock_safra_batch_search_use_case.list_rows_for_export.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_safra_batch_export_not_found(
    async_safra_client: AsyncClient,
    mock_safra_batch_search_use_case: AsyncMock,
    generate_uuid,
) -> None:
    mock_safra_batch_search_use_case.list_rows_for_export = AsyncMock(
        side_effect=SafraBatchSearchNotFoundException(),
    )
    url = _SAFRA_BATCH_EXPORT_TEMPLATE.format(job_id=generate_uuid)
    response = await async_safra_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['code'] == 'SAFRA_BATCH_SEARCH_NOT_FOUND'


@pytest.mark.asyncio
async def test_delete_safra_batch_job_records_success(
    async_safra_client: AsyncClient,
    mock_safra_batch_search_use_case: AsyncMock,
    generate_uuid,
) -> None:
    jid = generate_uuid
    mock_safra_batch_search_use_case.delete_persisted_batch_job_rows = AsyncMock(
        return_value=None,
    )
    url = _SAFRA_BATCH_DELETE_TEMPLATE.format(job_id=jid)
    response = await async_safra_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''
    mock_safra_batch_search_use_case.delete_persisted_batch_job_rows.assert_awaited_once_with(
        jid,
    )


@pytest.mark.asyncio
async def test_delete_safra_batch_job_not_found(
    async_safra_client: AsyncClient,
    mock_safra_batch_search_use_case: AsyncMock,
    generate_uuid,
) -> None:
    mock_safra_batch_search_use_case.delete_persisted_batch_job_rows = AsyncMock(
        side_effect=SafraBatchSearchNotFoundException(
            message='Nenhuma linha encontrada para esse lote.',
        ),
    )
    url = _SAFRA_BATCH_DELETE_TEMPLATE.format(job_id=generate_uuid)
    response = await async_safra_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['code'] == 'SAFRA_BATCH_SEARCH_NOT_FOUND'


@pytest.mark.asyncio
async def test_get_safra_financial_agreements(
    async_safra_client: AsyncClient,
    mock_safra_use_case: AsyncMock,
) -> None:
    financial_agreements = [
        FinancialAgreementResponse(
            idConvenio=1,
            nome='N',
            cnpj=SAFRA_TEST_CNPJ,
            nomeFantasia='NF',
            uf='SP',
        )
    ]
    mock_safra_use_case.get_financial_agreements = AsyncMock(
        return_value=financial_agreements
    )
    response = await async_safra_client.get(_SAFRA_FINANCIAL_AGREEMENTS)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [fa.model_dump() for fa in financial_agreements]
    mock_safra_use_case.get_financial_agreements.assert_awaited_once()
    assert response.json()[0]['nome'] == 'N'
    assert response.json()[0]['cnpj'] == SAFRA_TEST_CNPJ
    assert response.json()[0]['nomeFantasia'] == 'NF'
    assert response.json()[0]['uf'] == 'SP'
