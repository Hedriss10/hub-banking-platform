from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.service.safra import SafraService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_delegates_to_repository() -> None:
    repo = AsyncMock()
    repo.get_token = AsyncMock(
        return_value=TokenResponse.model_validate({'token': 'abc'})
    )
    service = SafraService(repo)
    out = await service.get_token()
    assert out.token == 'abc'
    repo.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_bankers_delegates_to_repository() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='X',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    repo = AsyncMock()
    repo.get_bankers = AsyncMock(return_value=bankers)
    service = SafraService(repo)
    out = await service.get_bankers()
    assert out == bankers
    repo.get_bankers.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_margem_bpo_delegates_to_repository() -> None:
    dto_in = MargemBpoDto(
        convenio=1,
        cpf=12345678901,
        idProduto=2,
        matricula='M1',
    )
    dto_out = MargemBpoOutputDto(
        cpf='12345678901',
        margem=100.0,
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
    repo = AsyncMock()
    repo.get_margem_bpo = AsyncMock(return_value=dto_out)
    service = SafraService(repo)
    out = await service.get_margem_bpo(dto_in)
    assert out == dto_out
    repo.get_margem_bpo.assert_awaited_once_with(dto_in)
