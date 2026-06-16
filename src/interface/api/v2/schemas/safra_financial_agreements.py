from typing import Optional

from pydantic import BaseModel, ConfigDict


class FinancialAgreementOutSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idConvenio: Optional[int] = None
    nome: Optional[str] = None
    cnpj: Optional[int] = None
    nomeFantasia: Optional[str] = None
    uf: Optional[str] = None
