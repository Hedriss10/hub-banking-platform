from typing import Optional

from pydantic import BaseModel, ConfigDict


class _ContractSummaryMixin(BaseModel):
    nrCpfCliente: Optional[str] = None
    nrContrato: Optional[str] = None
    dtHoraInclusao: Optional[str] = None
    dsStatusContrato: Optional[str] = None
    dsSituacaoContrato: Optional[str] = None
    qtPendencias: Optional[int] = None
    dsMotivoRecusaPortabilidade: Optional[str] = None


class ContractRegistrationDataDto(_ContractSummaryMixin):
    model_config = ConfigDict(extra='ignore')

    dsUsuarioInclusao: Optional[str] = None
    nmUsuarioInclusao: Optional[str] = None
    cdLoja: Optional[int] = None
    nmLoja: Optional[str] = None
    cdSub: Optional[int] = None
    nmSub: Optional[str] = None
    cdConvenio: Optional[int] = None
    nmConvenio: Optional[str] = None
    nmCliente: Optional[str] = None
    dtNascimentoCliente: Optional[str] = None
    nrRgCliente: Optional[str] = None
    dsEstadoCivilCliente: Optional[str] = None
    dsSexoCliente: Optional[str] = None
    nmMaeCliente: Optional[str] = None
    nmPaiCliente: Optional[str] = None
    cdProduto: Optional[str] = None
    cdMatricula: Optional[str] = None
    nrCpfPromotor: Optional[str] = None
    dsEnderecoLogradouro: Optional[str] = None
    dsEnderecoNumero: Optional[str] = None
    dsEnderecoComplemento: Optional[str] = None
    dsEnderecoBairro: Optional[str] = None
    dsEnderecoCidade: Optional[str] = None
    dsEnderecoUf: Optional[str] = None
    dsEnderecoCep: Optional[int] = None
    nrTelefoneDDD: Optional[str] = None
    nrTelefoneNumero: Optional[int] = None
    nrCelularDDD: Optional[str] = None
    nrCelularNumero: Optional[int] = None
    vlRendaMensalCliente: Optional[float] = None
    isRefinPortabilidade: Optional[bool] = None


class ContractLoanDto(_ContractSummaryMixin):
    model_config = ConfigDict(extra='ignore')

    vlRefinanciado: Optional[float] = None
    vlEmprestimo: Optional[float] = None
    vlPrestacao: Optional[float] = None
    qtPrestacao: Optional[int] = None
    dtLiberacao: Optional[str] = None
    dsTabelaJuros: Optional[str] = None
    pcTaxaJuros: Optional[float] = None
    vlTac: Optional[float] = None
    idPropostaOrigem: Optional[int] = None
    isPortabilidadeFinalizada: Optional[bool] = None
    vlRCO: Optional[float] = None


class ContractFinancialDto(_ContractSummaryMixin):
    model_config = ConfigDict(extra='ignore')

    dtPagtoDivida: Optional[str] = None
    dtPagtoTroco: Optional[str] = None
    dtPagtoComissao: Optional[str] = None
    vlComisssao: Optional[float] = None
    vlDivida: Optional[float] = None
    vlTroco: Optional[float] = None
    dsBancoCliente: Optional[int] = None
    dsAgenciaCliente: Optional[int] = None
    dsDigitoAgenciaCliente: Optional[str] = None
    dsContaCliente: Optional[int] = None
    dsDigitoContaCliente: Optional[str] = None
    cdRetornoDataprev: Optional[str] = None
    dtRetornoDataprev: Optional[str] = None
    nrArquivoRetornoDataprev: Optional[int] = None
    vlLiquidacaoReembolso: Optional[float] = None
    vlLiquidacaoBoleto: Optional[float] = None
    vlLiquidacaoStr: Optional[float] = None


class ContractStatusDto(_ContractSummaryMixin):
    model_config = ConfigDict(extra='ignore')
