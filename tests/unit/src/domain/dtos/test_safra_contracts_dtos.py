import pytest
from src.domain.dtos.safra_calculation import CalculationRequestDto, CalculationResponseDto
from src.domain.dtos.safra_contracts import (
    ContractFinancialDto,
    ContractLoanDto,
    ContractRegistrationDataDto,
    ContractStatusDto,
)
from src.domain.use_case.safra import SafraUseCase

pytestmark = pytest.mark.unit


def test_contract_registration_data_parses_optional_fields() -> None:
    dto = ContractRegistrationDataDto.model_validate({
        'nrCpfCliente': '123',
        'dsMotivoRecusaPortabilidade': 'motivo',
        'isRefinPortabilidade': True,
    })
    assert dto.isRefinPortabilidade is True
    assert dto.dsMotivoRecusaPortabilidade == 'motivo'


def test_contract_loan_parses_optional_fields() -> None:
    dto = ContractLoanDto.model_validate({
        'nrContrato': '99',
        'vlRCO': 10.5,
        'isPortabilidadeFinalizada': False,
    })
    assert dto.vlRCO == 10.5


def test_contract_financial_parses_optional_fields() -> None:
    dto = ContractFinancialDto.model_validate({
        'nrCpfCliente': '123',
        'vlLiquidacaoStr': 100.0,
    })
    assert dto.vlLiquidacaoStr == 100.0


def test_contract_status_parses_mixin_fields() -> None:
    dto = ContractStatusDto.model_validate({
        'nrCpfCliente': '123',
        'qtPendencias': 2,
    })
    assert dto.qtPendencias == 2


@pytest.mark.asyncio
async def test_use_case_post_calculo_novo_delegates_to_service() -> None:
    from unittest.mock import AsyncMock

    dto_in = CalculationRequestDto(idConvenio=1, cpf=12345678901, comSeguro=False)
    expected = CalculationResponseDto(criticas=[], avisos=[])
    service = AsyncMock()
    service.post_calculo_novo = AsyncMock(return_value=expected)
    use_case = SafraUseCase(service)

    result = await use_case.post_calculo_novo(dto_in)

    assert result == expected
    service.post_calculo_novo.assert_awaited_once_with(dto_in)
