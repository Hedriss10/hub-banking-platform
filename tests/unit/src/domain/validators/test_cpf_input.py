import pytest
from src.domain.validators.cpf_input import normalize_brazilian_cpf_digits

pytestmark = pytest.mark.unit


def test_normalize_cpf_preserva_zeros_a_esquerda() -> None:
    assert normalize_brazilian_cpf_digits('01437872506') == '01437872506'


def test_normalize_cpf_remove_mascara() -> None:
    assert normalize_brazilian_cpf_digits('014.378.725-06') == '01437872506'


def test_normalize_cpf_excel_float_string() -> None:
    assert normalize_brazilian_cpf_digits('1437872506.0') == '01437872506'


def test_normalize_cpf_trunca_acima_de_onze_digitos() -> None:
    assert normalize_brazilian_cpf_digits('991437872506') == '91437872506'


def test_normalize_cpf_none_rejeita() -> None:
    with pytest.raises(ValueError, match='CPF não pode ser vazio'):
        normalize_brazilian_cpf_digits(None)


def test_normalize_cpf_complementa_dez_digitos() -> None:
    assert normalize_brazilian_cpf_digits('1234567890') == '01234567890'


@pytest.mark.parametrize(
    'bad',
    [
        ('',),
        ('123',),
        ('abcdefghijk',),
    ],
)
def test_normalize_cpf_invalido(bad: str) -> None:
    with pytest.raises(ValueError, match='CPF'):
        normalize_brazilian_cpf_digits(bad)
