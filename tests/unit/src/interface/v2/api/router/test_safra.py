from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from src.domain.dtos.safra import BankerResponse, MargemBpoOutputDto, TokenResponse
from starlette import status

pytestmark = pytest.mark.unit

_SAFRA_TOKEN = '/api/v2/safra/token'
_SAFRA_BANKS = '/api/v2/safra/banks'
_SAFRA_MARGIN_BPO = '/api/v2/safra/margin/bpo'


_MARGEM_OUT = MargemBpoOutputDto(
    cpf='12345678901',
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
        'cpf': 12345678901,
        'idProduto': 2,
        'matricula': 'M-01',
    }
    response = await async_safra_client.post(_SAFRA_MARGIN_BPO, json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['margem'] == _MARGEM_OUT.margem
    assert data['cpf'] == '12345678901'
    mock_safra_use_case.get_margem_bpo.assert_awaited_once()
