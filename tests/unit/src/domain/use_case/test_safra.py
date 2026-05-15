from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.use_case.safra import SafraUseCase
from tests.fixtures.safra_test_constants import SAFRA_TEST_CNPJ

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
            cnpj=SAFRA_TEST_CNPJ,
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
        cpf='12345678901',
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


@pytest.mark.asyncio
async def test_get_financial_agreements() -> None:
    financial_agreements = [
        FinancialAgreementResponse(
            idConvenio=1,
            nome='N',
            cnpj=SAFRA_TEST_CNPJ,
            nomeFantasia='NF',
            uf='SP',
        )
    ]
    service = AsyncMock()
    service.get_financial_agreements = AsyncMock(return_value=financial_agreements)
    uc = SafraUseCase(service)
    out = await uc.get_financial_agreements()
    assert out == financial_agreements
    service.get_financial_agreements.assert_awaited_once()
    assert out[0].idConvenio == 1
    assert out[0].nome == 'N'
    assert out[0].cnpj == SAFRA_TEST_CNPJ
    assert out[0].nomeFantasia == 'NF'
    assert out[0].uf == 'SP'
