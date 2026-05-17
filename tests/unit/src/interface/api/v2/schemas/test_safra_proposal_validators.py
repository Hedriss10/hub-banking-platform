import pytest
from pydantic import ValidationError
from src.interface.api.v2.schemas.safra_proposal import AddressSchema, BankDetailsSchema

pytestmark = pytest.mark.unit


def test_bank_schema_strips_non_empty_tipo_conta() -> None:
    b = BankDetailsSchema(tipoConta='  Corrente  ')
    assert b.tipoConta == 'Corrente'


def test_bank_schema_rejects_blank_tipo_conta() -> None:
    with pytest.raises(ValidationError):
        BankDetailsSchema(tipoConta='')


@pytest.mark.parametrize(
    ('cep_in', 'expected_digits'),
    [
        ('01310-100', '01310100'),
        ('01310100', '01310100'),
        (31314000, '31314000'),
    ],
)
def test_address_schema_cep_normalized(cep_in, expected_digits) -> None:
    a = AddressSchema(
        logradouro='L',
        numero='1',
        cep=cep_in,
        cidade='C',
        uf='MG',
    )
    assert a.cep == expected_digits


@pytest.mark.parametrize('bad_cep', [None, 1234567])
def test_address_schema_cep_invalid(bad_cep) -> None:
    with pytest.raises(ValidationError):
        AddressSchema(
            logradouro='L',
            numero='1',
            cep=bad_cep,
            cidade='C',
            uf='MG',
        )


def test_address_schema_uf_normalized() -> None:
    a = AddressSchema(
        logradouro='L',
        numero='1',
        cep='30130000',
        cidade='BH',
        uf=' MG ',
    )
    assert a.uf == 'MG'


@pytest.mark.parametrize('bad_uf', ['A', 'MGS'])
def test_address_schema_uf_invalid(bad_uf) -> None:
    with pytest.raises(ValidationError):
        AddressSchema(
            logradouro='L',
            numero='1',
            cep='30130000',
            cidade='C',
            uf=bad_uf,
        )
