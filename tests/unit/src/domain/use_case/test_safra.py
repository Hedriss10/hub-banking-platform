from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.use_case.safra import SafraUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token() -> None:
    service = AsyncMock()
    service.get_token = AsyncMock(
        return_value=TokenResponse.model_validate({'token': 'abc'})
    )
    uc = SafraUseCase(service)
    out = await uc.get_token()
    assert out.token == 'abc'
    service.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_bankers() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='X',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    service = AsyncMock()
    service.get_bankers = AsyncMock(return_value=bankers)
    uc = SafraUseCase(service)
    out = await uc.get_bankers()
    assert out == bankers
    service.get_bankers.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_margem_bpo() -> None:
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
    service = AsyncMock()
    service.get_margem_bpo = AsyncMock(return_value=dto_out)
    uc = SafraUseCase(service)
    out = await uc.get_margem_bpo(dto_in)
    assert out == dto_out
    service.get_margem_bpo.assert_awaited_once_with(dto_in)
