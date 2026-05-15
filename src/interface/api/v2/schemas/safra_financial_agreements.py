from pydantic import BaseModel


class FinancialAgreementOutSchema(BaseModel):
    idConvenio: int
    nome: str
    cnpj: int
    nomeFantasia: str
    uf: str
