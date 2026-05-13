"""
Cenários demonstrativos da integração Safra (consulta de margem BPO).

Uso típico: validação com stakeholders, mocks ou pré-visualização do payload.

No repositório, o cenário demo roda quando `DEBUG` está True ou
`API_SAFRA_MARGIN_RESPONSE_EMULATOR`, desde que `matches_demo_margin_bpo_request`
seja verdadeiro.
"""

from pydantic import BaseModel, ConfigDict

from src.domain.dtos.safra import MargemBpoDto, MargemBpoOutputDto

# CPF demo (consulta margem bem-sucedida simulada)
DEMO_MARGIN_SUCCESS_CPF: str = '38585766034'

# DEMO: convênio, produto e matrícula (fingerprint junto ao CPF)
DEMO_MARGIN_CONVENIO: int = 10237
DEMO_MARGIN_ID_PRODUTO: int = 1
DEMO_MARGIN_MATRICULA: str = '303048269980000'


class MargemBpoDemoResponseSchema(BaseModel):
    """Modelo da resposta JSON de consulta de margem (cenário demo)."""

    model_config = ConfigDict(extra='ignore')

    cpf: str
    margem: float
    lotacao: str
    autorizada: bool
    nome: str
    secretaria: str
    tipoServidor: str
    cargo: str
    regimeJuridico: str
    dataAdmissao: str
    uf: str
    renda: float
    mensagemErro: str
    dataHoraConsulta: str


def margin_bpo_success_demo_example() -> MargemBpoDemoResponseSchema:
    """Payload fixo de sucesso (mesma forma que o retorno esperado da API)."""
    return MargemBpoDemoResponseSchema(
        cpf=DEMO_MARGIN_SUCCESS_CPF,
        margem=1599.0477654811452,
        lotacao='Lotação demonstração CEO',
        autorizada=False,
        nome='Servidor Demonstração',
        secretaria='Secretaria de Estado - Demo',
        tipoServidor='Efetivo',
        cargo='Analista de Demonstração',
        regimeJuridico='Regime próprio municipal',
        dataAdmissao='2018-09-02T03:54:20.657Z',
        uf='SP',
        renda=3921.951769465286,
        mensagemErro='',
        dataHoraConsulta='1962-05-14T08:57:38.359Z',
    )


def margin_bpo_success_as_domain_dto() -> MargemBpoOutputDto:
    """Converte o exemplo demo para o DTO de domínio usado no repositório."""
    demo = margin_bpo_success_demo_example()
    return MargemBpoOutputDto.model_validate(demo.model_dump(mode='json'))


def _normalize_cpf(value: str | int) -> str:
    digits = ''.join(c for c in str(value) if c.isdigit())
    return digits


def try_resolve_margin_bpo_demo(cpf: str | int) -> MargemBpoOutputDto | None:
    """
    Se o CPF for o demo acordado, devolve o DTO de sucesso; caso contrário None.

    Aceita entrada com ou sem máscara.
    """
    if _normalize_cpf(cpf) == DEMO_MARGIN_SUCCESS_CPF:
        return margin_bpo_success_as_domain_dto()
    return None


def matches_demo_margin_bpo_request(dto: MargemBpoDto) -> bool:
    """True quando o POST de margem coincide com o payload demo (CEO / homologação)."""
    return (
        _normalize_cpf(dto.cpf) == DEMO_MARGIN_SUCCESS_CPF
        and dto.convenio == DEMO_MARGIN_CONVENIO
        and dto.idProduto == DEMO_MARGIN_ID_PRODUTO
        and dto.matricula.strip() == DEMO_MARGIN_MATRICULA
    )


def try_resolve_margin_bpo_demo_request(
    dto: MargemBpoDto,
) -> MargemBpoOutputDto | None:
    """Se o request inteiro é o cenário demo, devolve margem simulada; senão None."""
    if matches_demo_margin_bpo_request(dto):
        return margin_bpo_success_as_domain_dto()
    return None
