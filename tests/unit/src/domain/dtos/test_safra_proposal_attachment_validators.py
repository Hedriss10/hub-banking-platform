import pytest
from pydantic import ValidationError
from src.domain.dtos.safra_proposal_attachment import ProposalAttachmentDto
from src.interface.api.v2.schemas.safra_proposal_attachment import (
    ProposalAttachmentInSchema,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    'dto_cls',
    [ProposalAttachmentDto, ProposalAttachmentInSchema],
)
@pytest.mark.parametrize(
    'field,value',
    [
        ('nomeArquivo', '   '),
        ('conteudoArquivo', '   '),
    ],
)
def test_attachment_validators_reject_blank_strings(
    dto_cls: type,
    field: str,
    value: str,
) -> None:
    payload = {
        'idDocumento': 1,
        'nomeArquivo': 'doc.pdf',
        'conteudoArquivo': 'data',
        field: value,
    }
    with pytest.raises(ValidationError):
        dto_cls.model_validate(payload)
