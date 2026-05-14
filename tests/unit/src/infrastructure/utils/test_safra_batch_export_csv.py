from uuid import UUID

import pytest
from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.infrastructure.utils.safra_batch_export_csv import (
    encode_safra_batch_search_export_csv,
)

pytestmark = pytest.mark.unit


def test_export_csv_utf8_sig_and_semicolon() -> None:
    jid = UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    rows = [
        SafraBatchSearchExportRowDTO(
            batch_job_id=jid,
            cpf='01437872506',
            margem=1.25,
            lotacao='L',
            autorizada=True,
            nome='N',
            secretaria='S',
            tipoServidor='T',
            cargo=None,
            regimeJuridico=None,
            dataAdmissao=None,
            uf='SP',
            renda=100.5,
            phone_one=None,
            phone_two=None,
            phone_three=None,
            phone_four=None,
            phone_five=None,
        ),
    ]
    raw = encode_safra_batch_search_export_csv(rows)
    assert raw.startswith('\ufeff'.encode('utf-8'))
    decoded = raw.decode('utf-8-sig').split('\r\n')
    assert ';' in decoded[0]
    assert decoded[1].startswith(str(jid))
    assert ';true;' in decoded[1]
