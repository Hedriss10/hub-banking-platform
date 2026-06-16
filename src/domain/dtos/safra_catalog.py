from typing import Optional

from pydantic import BaseModel, ConfigDict


class SafraAgencyDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idBancoComercial: int
    idAgenciaComercial: int
    descricao: Optional[str] = None


class SafraPositionDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idCargo: int
    descricao: Optional[str] = None


class SafraEmploymentBondDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: Optional[int] = None
    descricao: Optional[str] = None


class SafraInterestTableBandDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idFaixa: Optional[int] = None
    idTabelaJuros: Optional[int] = None
    prazoInicial: Optional[int] = None
    prazoFinal: Optional[int] = None
    valorFinanciamentiMinimo: Optional[float] = None
    valorFinanciamentiMaximo: Optional[float] = None


class SafraOperationalGuideDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    idSetor: int
