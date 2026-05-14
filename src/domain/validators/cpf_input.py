"""Normalização de CPF para integrações que exigem string (ex.: API Safra / .NET)."""

from typing import Annotated

from pydantic import BeforeValidator

_CPF_LEN = 11
_CPF_PAD_FROM_LEN = 10


def normalize_brazilian_cpf_digits(value: object) -> str:
    """
    Converte entrada de CSV/API para string só com dígitos, com zeros à esquerda.

    Aceita texto com máscara; valores vindos do Excel como float são tratados pela
    parte inteira (atenção: float pode já ter perdido o zero inicial — nesse caso,
    opcionalmente completa até 11 dígitos).
    """
    if value is None:
        raise ValueError('CPF não pode ser vazio')

    raw = str(value).strip()
    if not raw:
        raise ValueError('CPF não pode ser vazio')

    # Formato tipo número Excel: apenas um "." e demais caracteres são dígitos
    if raw.count('.') == 1 and raw.replace('.', '').isdigit():
        raw = raw.split('.')[0]

    digits = ''.join(c for c in raw if c.isdigit())

    if len(digits) > _CPF_LEN:
        digits = digits[-_CPF_LEN:]

    if len(digits) == _CPF_PAD_FROM_LEN:
        digits = digits.zfill(_CPF_LEN)

    if len(digits) != _CPF_LEN:
        raise ValueError('CPF deve conter 11 dígitos')

    return digits


CpfSafraStr = Annotated[str, BeforeValidator(normalize_brazilian_cpf_digits)]
