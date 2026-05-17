from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
from src.domain.dtos.safra_tables import SafraTablesDto
from src.domain.service.safra import SafraService
from tests.fixtures.safra_proposal_min import minimal_safra_proposal_payload
from tests.fixtures.safra_test_constants import SAFRA_TEST_CNPJ, SAFRA_TEST_CPF

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
            cnpj=SAFRA_TEST_CNPJ,
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
    repo = AsyncMock()
    repo.get_margem_bpo = AsyncMock(return_value=dto_out)
    service = SafraService(repo)
    out = await service.get_margem_bpo(dto_in)
    assert out == dto_out
    repo.get_margem_bpo.assert_awaited_once_with(dto_in)


@pytest.mark.asyncio
async def test_get_financial_agreements_delegates_to_repository() -> None:
    financial_agreements = [
        FinancialAgreementResponse(
            idConvenio=1,
            nome='N',
            cnpj=SAFRA_TEST_CNPJ,
            nomeFantasia='NF',
            uf='SP',
        )
    ]
    repo = AsyncMock()
    repo.get_financial_agreements = AsyncMock(return_value=financial_agreements)
    service = SafraService(repo)
    out = await service.get_financial_agreements()
    assert out == financial_agreements
    repo.get_financial_agreements.assert_awaited_once()
    assert out[0].idConvenio == 1
    assert out[0].nome == 'N'
    assert out[0].cnpj == SAFRA_TEST_CNPJ
    assert out[0].nomeFantasia == 'NF'
    assert out[0].uf == 'SP'


@pytest.mark.asyncio
async def test_post_credit_lighthouse_delegates_to_repository() -> None:
    id_tipo_retorno = 7
    dto_in = CreditLighthouseDto(
        idConvenio=10237,
        idTipoProduto=1,
        cpf=SAFRA_TEST_CPF,
    )
    expected = [
        CreditLighthouseResponse(
            decisaoFarol=1,
            cpf=SAFRA_TEST_CPF,
            idTipoProduto=id_tipo_retorno,
            motivos=['OK'],
            timeOut=0,
        )
    ]
    repo = AsyncMock()
    repo.post_credit_lighthouse = AsyncMock(return_value=expected)
    service = SafraService(repo)
    out = await service.post_credit_lighthouse(dto_in)
    assert out == expected
    repo.post_credit_lighthouse.assert_awaited_once_with(dto_in)
    assert len(out) == 1
    assert out[0].decisaoFarol == 1
    assert out[0].cpf == SAFRA_TEST_CPF
    assert out[0].idTipoProduto == id_tipo_retorno


@pytest.mark.asyncio
async def test_list_safra_tables_delegates_to_repository() -> None:
    safra_tables = [
        SafraTablesDto(
            id=1,
            descricao='Descrição',
            dtInicioVigencia=datetime.now(),
            dtFimVigencia=datetime.now(),
        )
    ]
    repo = AsyncMock()
    repo.list_safra_tables = AsyncMock(return_value=safra_tables)
    service = SafraService(repo)
    out = await service.list_safra_tables(1)
    assert out == safra_tables
    repo.list_safra_tables.assert_awaited_once_with(1)
    assert len(out) == 1
    assert out[0].id == 1
    assert out[0].descricao == 'Descrição'


@pytest.mark.asyncio
async def test_post_safra_proposal_delegates_to_repository() -> None:
    dto_in = ProposalDto.model_validate(minimal_safra_proposal_payload())
    dto_out = ProposalResponseDto(idProposta=909)
    repo = AsyncMock()
    repo.post_safra_proposal = AsyncMock(return_value=dto_out)
    service = SafraService(repo)
    out = await service.post_safra_proposal(dto_in)
    assert out == dto_out
    repo.post_safra_proposal.assert_awaited_once_with(dto_in)
