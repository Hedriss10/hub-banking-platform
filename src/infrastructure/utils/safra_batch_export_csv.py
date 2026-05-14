import csv
from datetime import datetime
from io import StringIO
from typing import Optional

from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO

_HEADERS = (
    'batch_job_id',
    'cpf',
    'margem',
    'lotacao',
    'autorizada',
    'nome',
    'secretaria',
    'tipoServidor',
    'cargo',
    'regimeJuridico',
    'dataAdmissao',
    'uf',
    'renda',
    'phone_one',
    'phone_two',
    'phone_three',
    'phone_four',
    'phone_five',
)


def _cell_dt(value: Optional[datetime]) -> str:
    return value.isoformat() if value is not None else ''


def encode_safra_batch_search_export_csv(
    rows: list[SafraBatchSearchExportRowDTO],
) -> bytes:
    buffer = StringIO()
    writer = csv.writer(
        buffer,
        delimiter=';',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator='\r\n',
    )
    writer.writerow(list(_HEADERS))

    for r in rows:
        writer.writerow(
            (
                str(r.batch_job_id),
                r.cpf or '',
                '' if r.margem is None else str(r.margem),
                r.lotacao or '',
                '' if r.autorizada is None else ('true' if r.autorizada else 'false'),
                r.nome or '',
                r.secretaria or '',
                r.tipoServidor or '',
                r.cargo or '',
                r.regimeJuridico or '',
                _cell_dt(r.dataAdmissao),
                r.uf or '',
                '' if r.renda is None else str(r.renda),
                r.phone_one or '',
                r.phone_two or '',
                r.phone_three or '',
                r.phone_four or '',
                r.phone_five or '',
            ),
        )

    return buffer.getvalue().encode('utf-8-sig')
