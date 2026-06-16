from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CalculationRequestDto(BaseModel):
    """Alinha a CalculoPropostaRequest da API Safra (produto Novo)."""

    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    cpf: int
    comSeguro: bool
    idUF: Optional[str] = None
    matricula: Optional[str] = None
    prazos: Optional[List[int]] = None
    idCorban: Optional[int] = None
    idCorbansubs: Optional[int] = None
    idComercial: Optional[int] = None
    isCotacao: Optional[bool] = None
    idTabelaJuros: Optional[int] = None
    taxaJuros: Optional[float] = None
    tarifaCadastro: Optional[float] = None
    idSeguro: Optional[int] = None
    valorPrincipal: Optional[float] = None
    valorParcela: Optional[float] = None
    prazo: Optional[int] = None
    comissao: Optional[float] = None
    idServicos: Optional[List[int]] = None
    dataAdmissao: Optional[str] = None
    valorRenda: Optional[float] = None
    valorDescontos: Optional[float] = None
    idSituacaoEmpregado: Optional[int] = None
    idSexo: Optional[str] = None
    dtNascimento: Optional[datetime] = None


class SimulationDataDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: Optional[int] = None
    vencimento: Optional[datetime] = None
    idTabelaJuros: Optional[int] = None
    dsTabelaJuros: Optional[str] = None
    prazo: Optional[int] = None
    tarifaCadastro: Optional[float] = None
    valorParcela: Optional[float] = None
    valorPrincipal: Optional[float] = None
    valorDivida: Optional[float] = None
    valorRefin: Optional[float] = None
    valorTroco: Optional[float] = None
    taxaJuros: Optional[float] = None
    taxaJurosAno: Optional[float] = None
    ultimoVencimento: Optional[datetime] = None
    valorSeguro: Optional[float] = None
    valorFinanciado: Optional[float] = None
    valorIof: Optional[float] = None
    valorIofAdicional: Optional[float] = None
    valorIofComplementar: Optional[float] = None
    pcCet: Optional[float] = None
    pcCetAno: Optional[float] = None


class CalculationResponseDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    dataSimulacao: Optional[datetime] = None
    simulacoes: Optional[List[SimulationDataDto]] = None
    criticas: Optional[List[str]] = None
    avisos: Optional[List[str]] = None


class RefinDetailDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idContrato: int


class CalculationRefinRequestDto(BaseModel):
    """Alinha a CalculoPropostaRefinRequest da API Safra."""

    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    cpf: int
    comSeguro: bool
    valorMargemAdicional: float
    idUF: Optional[str] = None
    matricula: Optional[str] = None
    prazos: Optional[List[int]] = None
    idCorban: Optional[int] = None
    idCorbansubs: Optional[int] = None
    idComercial: Optional[int] = None
    isCotacao: Optional[bool] = None
    idTabelaJuros: Optional[int] = None
    taxaJuros: Optional[float] = None
    tarifaCadastro: Optional[float] = None
    idSeguro: Optional[int] = None
    valorPrincipal: Optional[float] = None
    valorParcela: Optional[float] = None
    prazo: Optional[int] = None
    comissao: Optional[float] = None
    idServicos: Optional[List[int]] = None
    dataAdmissao: Optional[str] = None
    valorRenda: Optional[float] = None
    valorDescontos: Optional[float] = None
    idSituacaoEmpregado: Optional[int] = None
    idSexo: Optional[str] = None
    dtNascimento: Optional[datetime] = None
    valorTroco: Optional[float] = None
    refins: Optional[List[RefinDetailDto]] = None


class CalculationPortabilityRequestDto(BaseModel):
    """Alinha a CalculoPropostaPortabRequest da API Safra."""

    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    cpf: int
    comSeguro: bool
    idUF: Optional[str] = None
    matricula: Optional[str] = None
    prazos: Optional[List[int]] = None
    idCorban: Optional[int] = None
    idCorbansubs: Optional[int] = None
    idComercial: Optional[int] = None
    isCotacao: Optional[bool] = None
    idTabelaJuros: Optional[int] = None
    taxaJuros: Optional[float] = None
    tarifaCadastro: Optional[float] = None
    idSeguro: Optional[int] = None
    valorPrincipal: Optional[float] = None
    valorParcela: Optional[float] = None
    prazo: Optional[int] = None
    comissao: Optional[float] = None
    idServicos: Optional[List[int]] = None
    dataAdmissao: Optional[str] = None
    valorRenda: Optional[float] = None
    valorDescontos: Optional[float] = None
    idSituacaoEmpregado: Optional[int] = None
    idSexo: Optional[str] = None
    dtNascimento: Optional[datetime] = None
    valorDivida: Optional[float] = None
    valorParcelaSimulacaoPortabilidade: Optional[float] = None
    prazoSimulacaoPortabilidade: Optional[int] = None


class PortabilitySimulationDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    valorParcelaContratoOrig: float
    valorDivida: float
    prazoTotalContratoOrig: int
    prazoRemanescenteContratoOrig: int
    taxaJuros: Optional[float] = None
    valorParcela: Optional[float] = None
    isCotacao: Optional[bool] = None


class RefinSimulationDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    prazos: Optional[List[int]] = None
    taxaJuros: Optional[float] = None
    valorTroco: Optional[float] = None
    valorParcela: Optional[float] = None
    isCotacao: Optional[bool] = None
    idTabelaJuros: Optional[int] = None
    idSeguro: Optional[int] = None
    comissao: Optional[float] = None
    tarifaCadastro: Optional[float] = None


class CalculationPortRefinRequestDto(BaseModel):
    """Alinha a CalculoPropostaPortRefinRequest da API Safra."""

    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    cpf: int
    simulacaoPortabilidade: PortabilitySimulationDto
    simulacaoRefin: RefinSimulationDto
    idSituacaoEmpregado: Optional[int] = None
    idSexo: Optional[str] = None
    dtNascimento: Optional[datetime] = None
    idUF: Optional[str] = None
    matricula: Optional[str] = None
    valorRenda: Optional[float] = None


class CalculationPortRefinResponseDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    dataSimulacao: Optional[datetime] = None
    simulacoesPortabilidade: Optional[List[SimulationDataDto]] = None
    simulacoesRefin: Optional[List[SimulationDataDto]] = None
    criticas: Optional[List[str]] = None
    avisos: Optional[List[str]] = None
