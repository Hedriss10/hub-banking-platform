from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreatedProposalDocumentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_path: Optional[str] = None
    proposal_id: Optional[UUID] = None
    created_by: UUID


class ProposalDocumentOutDTO(CreatedProposalDocumentDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
