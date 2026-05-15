from unittest.mock import AsyncMock, MagicMock, patch

import httpx
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
from src.infrastructure.repositories.safra_external import SafraExternalRepository
from src.infrastructure.seed import emulator_safra as emulator_safra_demo
from tests.fixtures.safra_test_constants import SAFRA_TEST_CNPJ, SAFRA_TEST_CPF

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_token_maps_response_json() -> None:
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {'token': 'jwt-here'}
    repo.api.get_token = AsyncMock(return_value=mock_resp)

    out = await repo.get_token()

    assert isinstance(out, TokenResponse)
    assert out.token == 'jwt-here'


@pytest.mark.asyncio
async def test_get_bankers_parses_rows() -> None:
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'data': [
            {
                'codigoBanco': 1,
                'nomeBanco': 'B',
                'cnpj': SAFRA_TEST_CNPJ,
                'ispb': 12345678,
            }
        ]
    }
    repo.api.get_bankers = AsyncMock(return_value=mock_resp)

    out = await repo.get_bankers()

    assert len(out) == 1
    assert isinstance(out[0], BankerResponse)
    assert out[0].nomeBanco == 'B'


@pytest.mark.asyncio
async def test_get_margem_bpo_maps_response_json() -> None:
    dto_in = MargemBpoDto(
        convenio=1,
        cpf='12345678901',
        idProduto=2,
        matricula='M1',
    )
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'cpf': '12345678901',
        'margem': 100.0,
        'lotacao': 'L',
        'autorizada': True,
        'nome': 'N',
        'secretaria': 'S',
        'tipoServidor': 'T',
        'cargo': 'C',
        'regimeJuridico': 'R',
        'dataAdmissao': '2020-01-01',
        'uf': 'SP',
        'renda': 5000.0,
        'mensagemErro': '',
        'dataHoraConsulta': '2026-01-01T00:00:00',
    }
    repo.api.get_margem_bpo = AsyncMock(return_value=mock_resp)

    out = await repo.get_margem_bpo(dto_in)
    float_margin = 100.0
    assert isinstance(out, MargemBpoOutputDto)
    assert out.margem == float_margin
    repo.api.get_margem_bpo.assert_awaited_once_with(dto_in)


@pytest.mark.asyncio
async def test_get_margem_bpo_demo_emulator_short_circuits_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto_in = MargemBpoDto(
        convenio=emulator_safra_demo.DEMO_MARGIN_CONVENIO,
        cpf=emulator_safra_demo.DEMO_MARGIN_SUCCESS_CPF,
        idProduto=emulator_safra_demo.DEMO_MARGIN_ID_PRODUTO,
        matricula=emulator_safra_demo.DEMO_MARGIN_MATRICULA,
    )
    mock_settings = MagicMock(API_SAFRA_MARGIN_RESPONSE_EMULATOR=True)
    monkeypatch.setattr(
        'src.infrastructure.repositories.safra_external.get_settings',
        lambda: mock_settings,
    )
    repo = SafraExternalRepository()
    spy = AsyncMock()
    repo.api.get_margem_bpo = spy
    expected = emulator_safra_demo.margin_bpo_success_as_domain_dto()

    out = await repo.get_margem_bpo(dto_in)

    assert out.margem == expected.margem
    spy.assert_not_called()


@pytest.mark.asyncio
async def test_get_margem_bpo_debug_on_triggers_demo_without_emulator_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto_in = MargemBpoDto(
        convenio=emulator_safra_demo.DEMO_MARGIN_CONVENIO,
        cpf=emulator_safra_demo.DEMO_MARGIN_SUCCESS_CPF,
        idProduto=emulator_safra_demo.DEMO_MARGIN_ID_PRODUTO,
        matricula=emulator_safra_demo.DEMO_MARGIN_MATRICULA,
    )
    mock_settings = MagicMock(
        API_SAFRA_MARGIN_RESPONSE_EMULATOR=False,
        DEBUG=True,
    )
    monkeypatch.setattr(
        'src.infrastructure.repositories.safra_external.get_settings',
        lambda: mock_settings,
    )
    repo = SafraExternalRepository()
    spy = AsyncMock()
    repo.api.get_margem_bpo = spy
    expected = emulator_safra_demo.margin_bpo_success_as_domain_dto()

    out = await repo.get_margem_bpo(dto_in)

    assert out.margem == expected.margem
    spy.assert_not_called()


@pytest.mark.asyncio
async def test_get_margem_bpo_demo_fingerprint_debug_emulator_off_calls_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dto_in = MargemBpoDto(
        convenio=emulator_safra_demo.DEMO_MARGIN_CONVENIO,
        cpf=emulator_safra_demo.DEMO_MARGIN_SUCCESS_CPF,
        idProduto=emulator_safra_demo.DEMO_MARGIN_ID_PRODUTO,
        matricula=emulator_safra_demo.DEMO_MARGIN_MATRICULA,
    )
    mock_settings = MagicMock(
        API_SAFRA_MARGIN_RESPONSE_EMULATOR=False,
        DEBUG=False,
    )
    monkeypatch.setattr(
        'src.infrastructure.repositories.safra_external.get_settings',
        lambda: mock_settings,
    )
    repo = SafraExternalRepository()
    margin_from_upstream = 999.0
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'cpf': emulator_safra_demo.DEMO_MARGIN_SUCCESS_CPF,
        'margem': margin_from_upstream,
        'lotacao': 'via-api',
        'autorizada': True,
        'nome': 'N',
        'secretaria': 'S',
        'tipoServidor': 'T',
        'cargo': 'C',
        'regimeJuridico': 'R',
        'dataAdmissao': '2020-01-01',
        'uf': 'SP',
        'renda': 1.0,
        'mensagemErro': '',
        'dataHoraConsulta': '2026-01-01T00:00:00',
    }
    spy = AsyncMock(return_value=mock_resp)
    repo.api.get_margem_bpo = spy

    out = await repo.get_margem_bpo(dto_in)

    assert out.margem == margin_from_upstream
    spy.assert_awaited_once_with(dto_in)


@pytest.mark.asyncio
async def test_get_margem_bpo_emulator_on_non_matching_payload_calls_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_settings = MagicMock(API_SAFRA_MARGIN_RESPONSE_EMULATOR=True)
    monkeypatch.setattr(
        'src.infrastructure.repositories.safra_external.get_settings',
        lambda: mock_settings,
    )
    dto_in = MargemBpoDto(
        convenio=1,
        cpf='38585766034',
        idProduto=1,
        matricula='other',
    )
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'cpf': '38585766034',
        'margem': 1.0,
        'lotacao': 'x',
        'autorizada': False,
        'nome': 'n',
        'secretaria': 's',
        'tipoServidor': 't',
        'cargo': 'c',
        'regimeJuridico': 'r',
        'dataAdmissao': '2020-01-01',
        'uf': 'SP',
        'renda': 1.0,
        'mensagemErro': '',
        'dataHoraConsulta': '2026-01-01T00:00:00',
    }
    repo.api.get_margem_bpo = AsyncMock(return_value=mock_resp)

    await repo.get_margem_bpo(dto_in)

    repo.api.get_margem_bpo.assert_awaited_once_with(dto_in)


@pytest.mark.asyncio
async def test_repository_instantiation_creates_api() -> None:
    with patch(
        'src.infrastructure.repositories.safra_external.SafraApi',
    ) as mock_cls:
        repo = SafraExternalRepository()
        mock_cls.assert_called_once()
        assert repo.api is mock_cls.return_value


@pytest.mark.asyncio
async def test_get_financial_agreements_maps_response_json() -> None:
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = [
        {
            'idConvenio': 1,
            'nome': 'N',
            'cnpj': SAFRA_TEST_CNPJ,
            'nomeFantasia': 'NF',
            'uf': 'SP',
        }
    ]
    repo.api.get_financial_agreements = AsyncMock(return_value=mock_resp)

    out = await repo.get_financial_agreements()

    assert len(out) == 1
    assert isinstance(out[0], FinancialAgreementResponse)
    assert out[0].idConvenio == 1
    assert out[0].nome == 'N'
    assert out[0].cnpj == SAFRA_TEST_CNPJ
    assert out[0].nomeFantasia == 'NF'
    assert out[0].uf == 'SP'


@pytest.mark.asyncio
async def test_post_credit_lighthouse_maps_list_json() -> None:
    dto_in = CreditLighthouseDto(
        idConvenio=10237,
        idTipoProduto=1,
        cpf=SAFRA_TEST_CPF,
    )
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = [
        {
            'decisaoFarol': 1,
            'cpf': SAFRA_TEST_CPF,
            'motivos': ['APROVADO'],
            'timeOut': 0,
        },
    ]
    repo.api.post_credit_lighthouse = AsyncMock(return_value=mock_resp)

    out = await repo.post_credit_lighthouse(dto_in)

    assert len(out) == 1
    assert isinstance(out[0], CreditLighthouseResponse)
    assert out[0].decisaoFarol == 1
    repo.api.post_credit_lighthouse.assert_awaited_once_with(dto_in)


@pytest.mark.asyncio
async def test_post_credit_lighthouse_wraps_single_object_json() -> None:
    dto_in = CreditLighthouseDto(
        idConvenio=1,
        idTipoProduto=2,
        cpf=12345678901,
    )
    repo = SafraExternalRepository()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.json.return_value = {
        'decisaoFarol': 0,
        'cpf': 12345678901,
        'motivos': [],
        'timeOut': 1,
        'extraIgnored': True,
    }
    repo.api.post_credit_lighthouse = AsyncMock(return_value=mock_resp)

    out = await repo.post_credit_lighthouse(dto_in)

    assert len(out) == 1
    assert out[0].decisaoFarol == 0
    assert out[0].timeOut == 1
