from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FormalizationTrackingDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: int
    dsFase: Optional[str] = None
    dtFase: str
    flFase: Optional[str] = None


class ProposalFlowStepDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: Optional[int] = None
    nmUsuario: Optional[str] = None
    dsLogin: Optional[str] = None
    dtInicio: Optional[str] = None
    dtFim: Optional[str] = None
    evento: Optional[str] = None
    detalhe: Optional[str] = None
    ordem: Optional[float] = None


class ProposalListQueryDto(BaseModel):
    """Query de GET /Propostas — parâmetros em PascalCase na API Safra."""

    model_config = ConfigDict(extra='ignore', populate_by_name=True)

    id_proposta: Optional[int] = Field(default=None, serialization_alias='IdProposta')
    id_cliente: Optional[int] = Field(default=None, serialization_alias='IdCliente')
    dt_inicio: Optional[datetime] = Field(default=None, serialization_alias='DtInicio')
    dt_fim: Optional[datetime] = Field(default=None, serialization_alias='DtFim')
    id_convenio: Optional[int] = Field(default=None, serialization_alias='IdConvenio')
    id_situacao: Optional[int] = Field(default=None, serialization_alias='IdSituacao')
    id_tp_produto: Optional[int] = Field(
        default=None, serialization_alias='IdTpProduto'
    )

    def to_query(self) -> dict[str, object]:
        return self.model_dump(mode='json', exclude_none=True, by_alias=True)


class ProposalListItemDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: Optional[int] = None
    idTabelaJuros: Optional[int] = None
    dsTabelaJuros: Optional[str] = None
    dataDigitacao: Optional[str] = None
    idStatus: Optional[int] = None
    status: Optional[str] = None
    idSituacao: Optional[int] = None
    situacao: Optional[str] = None
    idSubStatus: Optional[int] = None
    subStatus: Optional[str] = None
    idConvenio: Optional[int] = None
    convenio: Optional[str] = None
    uf: Optional[str] = None
    idProduto: Optional[int] = None
    produto: Optional[str] = None
    idCotacaoDecisao: Optional[int] = None
    dsCotacaoDecisao: Optional[str] = None
    idUsuario: Optional[int] = None
    dsLogin: Optional[str] = None
    idCorban: Optional[int] = None
    nmCorban: Optional[str] = None
    idCorbanSub: Optional[int] = None
    nmCorbanOrigem: Optional[str] = None
    corOrigem: Optional[int] = None
    origem: Optional[str] = None
    idTpFormalizacao: Optional[int] = None
    dsTpFormalizacao: Optional[str] = None
    idTpSituacaoFormalizacao: Optional[int] = None
    dsTooltipFormalizacao: Optional[str] = None
    cpfAgenteCertificado: Optional[int] = None
    nomeAgenteCertificado: Optional[str] = None
    dtValidadeAgenteCertificado: Optional[str] = None
    qtPrazo: Optional[int] = None
    valor: Optional[float] = None
    vlPrincipal: Optional[float] = None
    vlLimiteCartao: Optional[float] = None
    vlSaqueCartao: Optional[float] = None
    dtPrimeiroVencimento: Optional[str] = None
    dtUltimoVencimento: Optional[str] = None
    vlTroco: Optional[float] = None
    vlParcela: Optional[float] = None
    vlSeguro: Optional[float] = None
    cpf: Optional[int] = None
    nomeCliente: Optional[str] = None
    idBanco: Optional[int] = None
    nomeBanco: Optional[str] = None
    agenciaCliente: Optional[int] = None
    contaCliente: Optional[str] = None
    matricula: Optional[str] = None
    propostaAverbada: Optional[str] = None
    dtDecisao: Optional[str] = None
    dtAverbacao: Optional[str] = None
    dtPagamento: Optional[str] = None
    flNovoEntrante: Optional[str] = None
    dtLiberacaoTeimosinha: Optional[str] = None
    dtConcessaoBeneficio: Optional[str] = None
    dtPrevistaDesbloqueio: Optional[str] = None
    totalPendencias: Optional[int] = None
    qtdParcelas: Optional[int] = None
    idEmpresa: Optional[int] = None


class ParadinhaResponseDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idRetorno: Optional[int] = None
    dsRetorno: Optional[str] = None
