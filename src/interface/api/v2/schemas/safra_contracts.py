from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContractRegistrationDataOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nrCpfCliente: Optional[str] = None
    nrContrato: Optional[str] = None
    nmCliente: Optional[str] = None
    cdConvenio: Optional[int] = None
    nmConvenio: Optional[str] = None
    cdMatricula: Optional[str] = None
    dsStatusContrato: Optional[str] = None
    dsSituacaoContrato: Optional[str] = None
    qtPendencias: Optional[int] = None
    dtHoraInclusao: Optional[str] = None


class ContractLoanOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nrCpfCliente: Optional[str] = None
    nrContrato: Optional[str] = None
    vlEmprestimo: Optional[float] = None
    vlPrestacao: Optional[float] = None
    qtPrestacao: Optional[int] = None
    dsTabelaJuros: Optional[str] = None
    pcTaxaJuros: Optional[float] = None
    dsStatusContrato: Optional[str] = None
    dsSituacaoContrato: Optional[str] = None
    qtPendencias: Optional[int] = None
    dtHoraInclusao: Optional[str] = None


class ContractFinancialOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nrCpfCliente: Optional[str] = None
    nrContrato: Optional[str] = None
    vlDivida: Optional[float] = None
    vlTroco: Optional[float] = None
    vlComisssao: Optional[float] = None
    dsStatusContrato: Optional[str] = None
    dsSituacaoContrato: Optional[str] = None
    qtPendencias: Optional[int] = None
    dtHoraInclusao: Optional[str] = None


class ContractStatusOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nrCpfCliente: Optional[str] = None
    nrContrato: Optional[str] = None
    dsStatusContrato: Optional[str] = None
    dsSituacaoContrato: Optional[str] = None
    qtPendencias: Optional[int] = None
    dtHoraInclusao: Optional[str] = None
