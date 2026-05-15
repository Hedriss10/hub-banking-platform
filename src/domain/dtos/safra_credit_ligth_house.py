from typing import List

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CreditLighthouseDto(BaseModel):
    model_config = ConfigDict(extra='ignore')

    idConvenio: int
    idTipoProduto: int
    cpf: int


class CreditLighthouseResponse(BaseModel):
    """
    Resposta do Farol de Crédito (API Safra).
    Campos podem vir em camelCase ou PascalCase.
    """

    model_config = ConfigDict(extra='ignore', populate_by_name=True)

    decisaoFarol: int = Field(
        validation_alias=AliasChoices('decisaoFarol', 'DecisaoFarol'),
    )
    cpf: int = Field(validation_alias=AliasChoices('cpf', 'Cpf'))
    idTipoProduto: int | None = Field(
        default=None,
        validation_alias=AliasChoices('idTipoProduto', 'IdTipoProduto'),
    )
    motivos: List[str] = Field(
        validation_alias=AliasChoices('motivos', 'Motivos'),
    )
    timeOut: int = Field(
        validation_alias=AliasChoices('timeOut', 'TimeOut'),
    )
