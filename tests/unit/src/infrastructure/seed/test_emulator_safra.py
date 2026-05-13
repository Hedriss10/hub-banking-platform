import pytest
from src.domain.dtos.safra import MargemBpoDto, MargemBpoOutputDto
from src.infrastructure.seed import emulator_safra as emu

pytestmark = pytest.mark.unit


def _full_demo_margin_dto(**overrides):
    payload = {
        'convenio': emu.DEMO_MARGIN_CONVENIO,
        'cpf': int(emu.DEMO_MARGIN_SUCCESS_CPF),
        'idProduto': emu.DEMO_MARGIN_ID_PRODUTO,
        'matricula': emu.DEMO_MARGIN_MATRICULA,
    }
    payload.update(overrides)
    return MargemBpoDto.model_validate(payload)


def test_demo_cpf_returns_margem_dto() -> None:
    expected = emu.margin_bpo_success_demo_example()
    out = emu.try_resolve_margin_bpo_demo('38585766034')
    assert isinstance(out, MargemBpoOutputDto)
    assert out.cpf == emu.DEMO_MARGIN_SUCCESS_CPF
    assert out.margem == expected.margem
    assert out.renda == expected.renda


def test_demo_cpf_masked_still_matches() -> None:
    assert emu.try_resolve_margin_bpo_demo('385.857.660-34') is not None


def test_other_cpf_returns_none() -> None:
    assert emu.try_resolve_margin_bpo_demo('11111111111') is None


def test_matches_demo_full_margin_request() -> None:
    dto = _full_demo_margin_dto()
    assert emu.matches_demo_margin_bpo_request(dto)


def test_try_resolve_demo_request_full_payload() -> None:
    dto = _full_demo_margin_dto()
    out = emu.try_resolve_margin_bpo_demo_request(dto)
    assert out is not None
    assert out.cpf == emu.DEMO_MARGIN_SUCCESS_CPF


def test_demo_wrong_matricula_returns_none() -> None:
    dto = _full_demo_margin_dto(matricula='other')
    assert emu.try_resolve_margin_bpo_demo_request(dto) is None


def test_success_schema_round_trip() -> None:
    schema = emu.margin_bpo_success_demo_example()
    dto = MargemBpoOutputDto.model_validate(schema.model_dump(mode='json'))
    assert dto.cpf == emu.DEMO_MARGIN_SUCCESS_CPF
