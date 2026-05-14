import csv
import io
import unicodedata
from typing import Any

from pydantic import ValidationError

from src.core.exceptions.custom import SafraBatchCsvValidationError
from src.domain.dtos.safra import SafraBatchSearchDto

_HEADER_TO_FIELD: dict[str, str] = {
    'convenio': 'convenio',
    'id_produto': 'idProduto',
    'idproduto': 'idProduto',
    'cpf': 'cpf',
    'matricula': 'matricula',
    'phone_one': 'phone_one',
    'phone_two': 'phone_two',
    'phone_three': 'phone_three',
    'phone_four': 'phone_four',
    'phone_five': 'phone_five',
    'telefone_um': 'phone_one',
    'telefone_dois': 'phone_two',
    'telefone_tres': 'phone_three',
    'telefone_quatro': 'phone_four',
    'telefone_cinco': 'phone_five',
}

_REQUIRED_FIELDS = frozenset({'convenio', 'idProduto', 'cpf', 'matricula'})


def _normalize_header(raw: str) -> str:
    s = raw.strip().lstrip('\ufeff').lower().replace('-', '_')
    return ''.join(
        c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'
    )


def _row_dict(csv_row: dict[str | Any, str | Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for raw_key, raw_val in csv_row.items():
        header_key = _normalize_header(str(raw_key))
        field = _HEADER_TO_FIELD.get(header_key)
        if field is None:
            continue
        mapped[field] = raw_val
    return mapped


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s
    return ''


def _guess_csv_delimiter(text: str) -> str:
    """
    Escolhe `;` ou `,` conforme o cabeçalho.

    CSV europeu / Excel BR costuma usar ponto e vírgula.
    """
    first = _first_non_empty_line(text)
    if not first:
        return ','
    semicolons = first.count(';')
    commas = first.count(',')
    if semicolons > commas:
        return ';'
    if commas > semicolons:
        return ','
    return ','


def parse_safra_batch_csv(content: bytes) -> list[SafraBatchSearchDto]:
    """
    Lê CSV com cabeçalho (UTF-8 com BOM permitido).

    Delimitador: vírgula (`,`) ou ponto e vírgula (`;`), inferido pela primeira linha.

    Colunas obrigatórias: convenio, idProduto (ou id_produto), cpf, matricula.
    Telefones opcionais: phone_one … phone_five (ou telefone_um … telefone_cinco).
    """
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise SafraBatchCsvValidationError(['CSV deve estar em UTF-8']) from exc

    delimiter = _guess_csv_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        raise SafraBatchCsvValidationError(['CSV sem cabeçalho'])

    rows: list[SafraBatchSearchDto] = []
    errors: list[str] = []

    for idx, csv_row in enumerate(reader, start=2):
        if all((v is None or str(v).strip() == '') for v in csv_row.values()):
            continue

        mapped = _row_dict(csv_row)
        missing = sorted(_REQUIRED_FIELDS - frozenset(mapped.keys()))
        if missing:
            errors.append(
                f'Linha {idx}: colunas obrigatórias ausentes: {", ".join(missing)}'
            )
            continue

        try:
            rows.append(SafraBatchSearchDto.model_validate(mapped))
        except ValidationError as exc:
            flattened = '; '.join(str(item.get('msg', '')) for item in exc.errors())
            errors.append(f'Linha {idx}: {flattened}')

    if errors:
        raise SafraBatchCsvValidationError(errors)

    if not rows:
        raise SafraBatchCsvValidationError(['Nenhuma linha válida no CSV'])

    return rows
