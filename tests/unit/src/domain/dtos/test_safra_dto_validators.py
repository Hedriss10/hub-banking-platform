import pytest
from pydantic import ValidationError
from src.domain.dtos.safra import MargemBpoDto, SafraBatchSearchDto

pytestmark = pytest.mark.unit


def test_margem_bpo_rejeita_id_produto_invalido() -> None:
    with pytest.raises(ValidationError):
        MargemBpoDto(
            convenio=1,
            cpf='12345678901',
            idProduto=99,
            matricula='M',
        )


def test_batch_search_rejeita_id_produto_invalido() -> None:
    with pytest.raises(ValidationError):
        SafraBatchSearchDto(
            convenio=1,
            idProduto=3,
            cpf='12345678901',
            matricula='M',
        )


def test_batch_search_telefone_em_branco_vai_para_none() -> None:
    row = SafraBatchSearchDto(
        convenio=1,
        idProduto=1,
        cpf='12345678901',
        matricula='M',
        phone_one='   ',
    )
    assert row.phone_one is None
