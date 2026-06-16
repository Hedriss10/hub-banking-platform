from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class LeadDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idLead: Optional[str] = None
    dsTipoJornada: Optional[str] = None
    passo: Optional[int] = None
    dsPasso: Optional[str] = None
    observacaoAtendimento: Optional[str] = None
    cliente: Optional[dict[str, Any]] = None
    propostas: Optional[List[dict[str, Any]]] = None
    dtImportacao: Optional[str] = None


class LeadReturnUploadItemDto(BaseModel):
    """Alinha a LeadRetornoEPSRequest da API Safra."""

    model_config = ConfigDict(extra='ignore')

    idCliente: int
    idLead: Optional[str] = None
    nomeCliente: Optional[str] = None
    nrBeneficio: Optional[str] = None
    idProposta: Optional[int] = None
    dtArquivoLead: Optional[str] = None
    codCallCenter: Optional[str] = None
    idOperador: Optional[str] = None
    telefones: Optional[List[dict[str, Any]]] = None
    idLigacao: Optional[str] = None
    dtContato: Optional[str] = None
    hrContatoInicio: Optional[str] = None
    tempoEspera: Optional[str] = None
    hrContatoFim: Optional[str] = None
    statusLigacao: Optional[str] = None
    statusAtendimento: Optional[str] = None
    statusPolitica: Optional[str] = None
    idCorban: Optional[int] = None
    idCorbanSub: Optional[int] = None
    idUsuario: Optional[int] = None
    dtUpload: Optional[str] = None
