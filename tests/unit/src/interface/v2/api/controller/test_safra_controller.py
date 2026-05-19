from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.safra import BankerResponse, MargemBpoOutputDto, TokenResponse
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.schemas.safra import MargemBpoInSchema
from src.interface.api.v2.schemas.safra_credit_ligth_house import (
    CreditLighthouseInSchema,
)
from src.interface.api.v2.schemas.safra_employing_body import SafraEmployingBodySchema
from src.interface.api.v2.schemas.safra_proposal import ProposalSchema
from src.interface.api.v2.schemas.safra_tables import SafraTablesOutSchema
from tests.fixtures.safra_proposal_min import minimal_safra_proposal_payload
from tests.fixtures.safra_test_constants import SAFRA_TEST_CNPJ, SAFRA_TEST_CPF

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_returns_schema() -> None:
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.get_token = AsyncMock(return_value=TokenResponse.model_validate({'token': 'x'}))
    controller = SafraController(uc, batch_uc)
    out = await controller.get_token()
    assert out.token == 'x'
    uc.get_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_banks_returns_schemas() -> None:
    bankers = [
        BankerResponse(
            codigoBanco=1,
            nomeBanco='N',
            cnpj=SAFRA_TEST_CNPJ,
            ispb=12345678,
        )
    ]
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.get_bankers = AsyncMock(return_value=bankers)
    controller = SafraController(uc, batch_uc)
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
    batch_uc = AsyncMock()
    uc.get_margem_bpo = AsyncMock(return_value=dto_out)
    controller = SafraController(uc, batch_uc)
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


@pytest.mark.asyncio
async def test_list_financial_agreements_returns_schemas() -> None:
    financial_agreements = [
        FinancialAgreementResponse(
            idConvenio=1,
            nome='N',
            cnpj=SAFRA_TEST_CNPJ,
            nomeFantasia='NF',
            uf='SP',
        )
    ]
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.get_financial_agreements = AsyncMock(return_value=financial_agreements)
    controller = SafraController(uc, batch_uc)
    out = await controller.list_financial_agreements()
    assert len(out) == 1
    assert out[0].nome == 'N'
    assert out[0].cnpj == SAFRA_TEST_CNPJ
    assert out[0].nomeFantasia == 'NF'
    assert out[0].uf == 'SP'


@pytest.mark.asyncio
async def test_post_credit_lighthouse_returns_schemas() -> None:
    decisao_esperada = 3
    dto_list = [
        CreditLighthouseResponse(
            decisaoFarol=decisao_esperada,
            cpf=SAFRA_TEST_CPF,
            idTipoProduto=None,
            motivos=['X'],
            timeOut=0,
        ),
    ]
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.post_credit_lighthouse = AsyncMock(return_value=dto_list)
    controller = SafraController(uc, batch_uc)
    body = CreditLighthouseInSchema(
        idConvenio=10237,
        idTipoProduto=1,
        cpf=SAFRA_TEST_CPF,
    )
    out = await controller.post_credit_lighthouse(body)
    assert len(out) == 1
    assert out[0].decisaoFarol == decisao_esperada
    assert out[0].cpf == SAFRA_TEST_CPF
    uc.post_credit_lighthouse.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_safra_tables_returns_schemas() -> None:
    safra_tables = [
        SafraTablesOutSchema(
            id=1,
            descricao='Descrição',
            dtInicioVigencia=datetime.now(),
            dtFimVigencia=datetime.now(),
        )
    ]
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.list_safra_tables = AsyncMock(return_value=safra_tables)
    controller = SafraController(uc, batch_uc)
    out = await controller.list_safra_tables(1)
    assert len(out) == 1
    assert out[0].id == 1
    assert out[0].descricao == 'Descrição'


@pytest.mark.asyncio
async def test_post_safra_proposal_returns_response_schema() -> None:
    body = ProposalSchema.model_validate(minimal_safra_proposal_payload())
    dto_out = ProposalResponseDto(idProposta=606)
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.post_safra_proposal = AsyncMock(return_value=dto_out)
    controller = SafraController(uc, batch_uc)
    out = await controller.post_safra_proposal(body)
    assert out.idProposta == dto_out.idProposta
    uc.post_safra_proposal.assert_awaited_once_with(
        ProposalDto.model_validate(body.model_dump()),
    )


@pytest.mark.asyncio
async def test_get_employing_bodies_returns_schemas() -> None:
    employing_bodies = [
        SafraEmployingBodySchema(
            id=1,
            descricao='Descrição',
        )
    ]
    uc = AsyncMock()
    batch_uc = AsyncMock()
    uc.get_employing_bodies = AsyncMock(return_value=employing_bodies)
    controller = SafraController(uc, batch_uc)
    out = await controller.get_employing_bodies(1)
    assert len(out) == 1
    assert out[0].id == 1
    assert out[0].descricao == 'Descrição'
