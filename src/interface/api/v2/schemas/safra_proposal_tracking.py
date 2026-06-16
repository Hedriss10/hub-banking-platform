from typing import Optional

from pydantic import BaseModel, ConfigDict


class FormalizationTrackingOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: int
    dsFase: Optional[str] = None
    dtFase: str
    flFase: Optional[str] = None


class ProposalFlowStepOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: Optional[int] = None
    nmUsuario: Optional[str] = None
    dsLogin: Optional[str] = None
    dtInicio: Optional[str] = None
    dtFim: Optional[str] = None
    evento: Optional[str] = None
    detalhe: Optional[str] = None
    ordem: Optional[float] = None


class ProposalListItemOutSchema(BaseModel):
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
    cpf: Optional[int] = None
    nomeCliente: Optional[str] = None
    vlPrincipal: Optional[float] = None
    vlParcela: Optional[float] = None
    qtPrazo: Optional[int] = None
    totalPendencias: Optional[int] = None


class ParadinhaOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idRetorno: Optional[int] = None
    dsRetorno: Optional[str] = None
