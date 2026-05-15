from pydantic import BaseModel


class FinancialAgreementResponse(BaseModel):
    """
    Resposta da consulta de convenios financeiros (API Safra).
    """

    idConvenio: int
    nome: str
    cnpj: int
    nomeFantasia: str
    uf: str
