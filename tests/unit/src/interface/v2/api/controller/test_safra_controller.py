from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import BankerResponse, MargemBpoOutputDto, TokenResponse
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.schemas.safra import MargemBpoInSchema

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_returns_schema() -> None:
    uc = AsyncMock()
    uc.get_token = AsyncMock(return_value=TokenResponse.model_validate({'token': 'x'}))
    controller = SafraController(uc)
    out = await controller.get_token()
    assert out.token == 'x'
    uc.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_banks_returns_schemas() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='N',
            cnpj=12345678000190,
            ispb=12345678,
        )
    ]
    uc = AsyncMock()
    uc.get_bankers = AsyncMock(return_value=bankers)
    controller = SafraController(uc)
    out = await controller.list_banks()
    assert len(out) == 1
    assert out[0].nomeBanco == 'N'


@pytest.mark.asyncio
async def test_consult_margem_bpo_returns_schema() -> None:
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
    uc = AsyncMock()
    uc.get_margem_bpo = AsyncMock(return_value=dto_out)
    controller = SafraController(uc)
    body = MargemBpoInSchema(
        convenio=1,
        cpf='12345678901',
        idProduto=2,
        matricula='M1',
    )
    out = await controller.consult_margem_bpo(body)
    float_margin = 100.0
    assert out.margem == float_margin
    assert out.cpf == '12345678901'
    uc.get_margem_bpo.assert_awaited_once()
