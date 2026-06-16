from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FormalizationPhoneOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nrDDD: Optional[int] = None
    nrTelefone: Optional[int] = None


class FormalizationLinkOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idProposta: Optional[int] = None
    idCliente: Optional[int] = None
    link: Optional[str] = None
    idConvenio: Optional[int] = None
    idUsuario: Optional[int] = None
    dsUsuario: Optional[str] = None
    dtInclusao: Optional[datetime] = None
    idLoja: Optional[int] = None
    vlPrincipal: Optional[float] = None
    telefone: Optional[FormalizationPhoneOutSchema] = None
    flagReformalizacao: Optional[bool] = None
    linkReformalizacao: Optional[str] = None
    tpSituacaoFormalizacao: Optional[int] = None
    tpStatus: Optional[int] = None
    dsStatus: Optional[str] = None
    tpStatusSubs: Optional[int] = None
    dsStatusSubs: Optional[str] = None
