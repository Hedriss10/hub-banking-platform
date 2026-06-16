from pydantic import BaseModel, ConfigDict, field_validator


class ProposalAttachmentDto(BaseModel):
    """Alinha a PostDocumentoAnexoRequest da API Safra."""

    model_config = ConfigDict(extra='ignore')

    idDocumento: int
    nomeArquivo: str
    conteudoArquivo: str

    @field_validator('nomeArquivo')
    @classmethod
    def _nome_arquivo_nao_vazio(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError('nomeArquivo é obrigatório.')
        return name

    @field_validator('conteudoArquivo')
    @classmethod
    def _conteudo_nao_vazio(cls, v: str) -> str:
        content = v.strip()
        if not content:
            raise ValueError('conteudoArquivo é obrigatório.')
        return content
