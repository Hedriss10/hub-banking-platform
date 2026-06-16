from typing import Optional

from pydantic import BaseModel, ConfigDict


class SafraAgencyOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idBancoComercial: int
    idAgenciaComercial: int
    descricao: Optional[str] = None


class SafraPositionOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idCargo: int
    descricao: Optional[str] = None


class SafraEmploymentBondOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: Optional[int] = None
    descricao: Optional[str] = None


class SafraInterestTableBandOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idFaixa: Optional[int] = None
    idTabelaJuros: Optional[int] = None
    prazoInicial: Optional[int] = None
    prazoFinal: Optional[int] = None
    valorFinanciamentiMinimo: Optional[float] = None
    valorFinanciamentiMaximo: Optional[float] = None


class SafraOperationalGuideOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    idSetor: int
