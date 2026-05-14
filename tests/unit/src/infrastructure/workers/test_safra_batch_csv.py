import pytest
from src.core.exceptions.custom import SafraBatchCsvValidationError
from src.infrastructure.workers.safra_batch_csv import parse_safra_batch_csv

pytestmark = pytest.mark.unit

_CONVENIO_DEMO = 10237
_TWO_VALID_ROWS = 2


def test_parse_csv_linha_valida_com_zeros_no_cpf() -> None:
    raw = (
        f'convenio,idProduto,cpf,matricula\n'
        f'{_CONVENIO_DEMO},1,01437872506,303048269980000\n'
    )
    rows = parse_safra_batch_csv(raw.encode('utf-8'))
    assert len(rows) == 1
    assert rows[0].cpf == '01437872506'


def test_parse_csv_headers_acentuados() -> None:
    raw = (
        'Convênio,id_produto,CPF,matrícula\n'
        f'{_CONVENIO_DEMO},1,01437872506,303048269980000\n'
    )
    rows = parse_safra_batch_csv(raw.encode('utf-8'))
    assert rows[0].convenio == _CONVENIO_DEMO


def test_parse_csv_utf8_invalido() -> None:
    with pytest.raises(SafraBatchCsvValidationError, match='UTF-8'):
        parse_safra_batch_csv(b'\xff\xfe')


def test_parse_csv_sem_linhas_validas() -> None:
    raw = 'convenio,idProduto,cpf,matricula\n'
    with pytest.raises(SafraBatchCsvValidationError, match='Nenhuma linha'):
        parse_safra_batch_csv(raw.encode('utf-8'))


def test_parse_csv_sem_cabecalho_detectavel() -> None:
    with pytest.raises(SafraBatchCsvValidationError, match='sem cabeçalho'):
        parse_safra_batch_csv(b'')


def test_parse_csv_coluna_desconhecida_ignorada() -> None:
    raw = (
        'convenio,idProduto,cpf,matricula,extra_col\n'
        f'{_CONVENIO_DEMO},1,01437872506,M,z\n'
    )
    rows = parse_safra_batch_csv(raw.encode('utf-8'))
    assert len(rows) == 1


def test_parse_csv_linha_em_branco_ignorada() -> None:
    raw = f'convenio,idProduto,cpf,matricula\n\n{_CONVENIO_DEMO},1,01437872506,M\n'
    rows = parse_safra_batch_csv(raw.encode('utf-8'))
    assert len(rows) == 1


def test_parse_csv_linha_so_campos_vazios_ignorada() -> None:
    raw = (
        'convenio,idProduto,cpf,matricula\n'
        f'{_CONVENIO_DEMO},1,01437872506,A\n'
        ',,,\n'
        f'{_CONVENIO_DEMO},1,01437872506,B\n'
    )
    rows = parse_safra_batch_csv(raw.encode('utf-8'))
    assert len(rows) == _TWO_VALID_ROWS


def test_parse_csv_erro_validacao_celula() -> None:
    raw = 'convenio,idProduto,cpf,matricula\nabc,1,01437872506,M\n'
    with pytest.raises(SafraBatchCsvValidationError) as exc:
        parse_safra_batch_csv(raw.encode('utf-8'))
    assert 'Linha 2' in exc.value.messages[0]


def test_parse_csv_colunas_obrigatorias_ausentes() -> None:
    raw = 'cpf\n01437872506\n'
    with pytest.raises(SafraBatchCsvValidationError) as exc:
        parse_safra_batch_csv(raw.encode('utf-8'))
    assert 'obrigatórias ausentes' in exc.value.messages[0]
