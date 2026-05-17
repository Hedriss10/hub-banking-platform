from typing import Any, List, Optional

from pydantic import BaseModel, field_validator

CEP_BR_DIGIT_COUNT = 8
"""Quantidade de dígitos esperada para CEP sem máscara (formato brasileiro)."""

BRAZIL_UF_SIGLA_LENGTH = 2
"""Tamanho da sigla da UF brasileira."""


class ContactDto(BaseModel):
    ddd: Optional[int] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[bool] = None


class BankDetailsDto(BaseModel):
    agencia: Optional[int] = None
    banco: Optional[int] = None
    conta: Optional[str] = None
    tipoConta: str

    @field_validator('tipoConta')
    @classmethod
    def _tipo_conta_nao_vazio(cls, v: str) -> str:
        t = v.strip()
        if not t:
            msg = (
                'tipoConta é obrigatório (valor conforme dominio/string da API Safra).'
            )
            raise ValueError(msg)
        return t


class OccupationDetailsDto(BaseModel):
    idCargo: Optional[int] = None
    idOrgaoEmpregador: Optional[int] = None
    idProfissao: Optional[int] = None
    idRegimeJuridico: Optional[int] = None
    idSituacaoEmpregado: Optional[int] = None
    idTipoVinculoEmpregaticio: Optional[int] = None
    matricula: Optional[str] = None
    valorRenda: Optional[float] = None
    idTipoPagamentoBeneficio: Optional[int] = None
    idUFBeneficio: Optional[str] = None
    dataAdmissao: Optional[str] = None
    valorRendaLiquida: Optional[float] = None


class PersonalDetailsDto(BaseModel):
    alfabetizado: Optional[str] = None
    cpf: Optional[int] = None
    dataNascimento: Optional[str] = None
    nomeCompleto: Optional[str] = None
    nomeMae: Optional[str] = None
    sexo: Optional[str] = None
    email: Optional[str] = None


class ProposalDataDto(BaseModel):
    """Alinha a DadosPropostaNovoRequest da Safra: * = obrigatório no contrato."""

    idConvenio: int
    idTabelaJuros: int
    isCotacao: bool
    valorParcela: float
    prazo: int
    valorPrincipal: float
    cpfAgenteCertificado: int
    dataPrimeiroVencimento: str
    taxaJuros: Optional[float] = None
    comSeguro: Optional[bool] = None
    aumentoMargem: bool = False


class AddressDto(BaseModel):
    logradouro: str
    numero: str
    cep: str
    cidade: str
    uf: str
    bairro: Optional[str] = None
    complemento: Optional[str] = None

    @field_validator('cep', mode='before')
    @classmethod
    def _cep_para_digitos(cls, v: Any) -> str:
        if v is None:
            raise ValueError('cep é obrigatório.')
        digits = ''.join(c for c in str(v).strip() if c.isdigit())
        if len(digits) != CEP_BR_DIGIT_COUNT:
            msg = f'cep deve conter exatamente {CEP_BR_DIGIT_COUNT} dígitos.'
            raise ValueError(msg)
        return digits

    @field_validator('uf')
    @classmethod
    def _uf_sigla(cls, v: str) -> str:
        u = v.strip().upper()
        if len(u) != BRAZIL_UF_SIGLA_LENGTH:
            msg = f'uf deve ser a sigla com {BRAZIL_UF_SIGLA_LENGTH} letras.'
            raise ValueError(msg)
        return u


class PayrollAssignmentBankDetailsDto(BaseModel):
    bancoAverbacao: Optional[int] = None
    agenciaAverbacao: Optional[int] = None
    contaAverbacao: Optional[str] = None


class ProposalDto(BaseModel):
    contatos: List[ContactDto]
    dadosBancarios: BankDetailsDto
    dadosOcupacao: OccupationDetailsDto
    dadosPessoais: PersonalDetailsDto
    dadosProposta: ProposalDataDto
    endereco: AddressDto
    submeter: bool
    dadosBancariosAverbacao: PayrollAssignmentBankDetailsDto


class ErrorDto(BaseModel):
    codigo: Optional[int] = None
    descricao: Optional[str] = None


class ProposalResponseDto(BaseModel):
    idProposta: Optional[int] = None
    erro: Optional[ErrorDto] = None
