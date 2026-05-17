import pytest
from pydantic import ValidationError
from src.domain.dtos.safra_proposal import AddressDto, BankDetailsDto

pytestmark = pytest.mark.unit


def test_bank_details_strips_non_empty_tipo_conta() -> None:
    b = BankDetailsDto(tipoConta='  Poupanca  ')
    assert b.tipoConta == 'Poupanca'


def test_bank_details_rejects_blank_tipo_conta() -> None:
    with pytest.raises(ValidationError):
        BankDetailsDto(tipoConta='')


def test_bank_details_rejects_whitespace_only_tipo_conta() -> None:
    with pytest.raises(ValidationError):
        BankDetailsDto(tipoConta='   ')


@pytest.mark.parametrize(
    ('cep_in', 'expected_digits'),
    [
        ('01310-100', '01310100'),
        (13010100, '13010100'),
        ('01310100', '01310100'),
    ],
)
def test_address_cep_normalized(cep_in, expected_digits) -> None:
    a = AddressDto(
        logradouro='L',
        numero='1',
        cep=cep_in,
        cidade='C',
        uf='SP',
    )
    assert a.cep == expected_digits


@pytest.mark.parametrize('bad_cep', [None, '123', '01310', 1234567])
def test_address_cep_invalid(bad_cep) -> None:
    with pytest.raises(ValidationError):
        AddressDto(
            logradouro='L',
            numero='1',
            cep=bad_cep,
            cidade='C',
            uf='SP',
        )


def test_address_uf_normalized() -> None:
    a = AddressDto(
        logradouro='L',
        numero='1',
        cep='01310100',
        cidade='C',
        uf=' rj ',
    )
    assert a.uf == 'RJ'


@pytest.mark.parametrize('bad_uf', ['S', '', 'SSP'])
def test_address_uf_invalid(bad_uf) -> None:
    with pytest.raises(ValidationError):
        AddressDto(
            logradouro='L',
            numero='1',
            cep='01310100',
            cidade='C',
            uf=bad_uf,
        )
