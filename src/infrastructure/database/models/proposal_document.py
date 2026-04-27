from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class ProposalDocumentModel(BaseModelWithEmployee):
    __tablename__ = 'proposal_documents'

    proposal_id: Mapped[UUID] = mapped_column(
        ForeignKey('proposals.id'), nullable=False
    )
    document_path: Mapped[str] = mapped_column(String, nullable=False)
