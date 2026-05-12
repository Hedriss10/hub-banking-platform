from uuid import UUID

from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
    ProposalOutDTO,
    ProposalUpdateDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.repositories.proposal import IProposalRepository


class ProposalService:
    def __init__(self, proposal_repository: IProposalRepository):
        self.proposal_repository = proposal_repository

    async def get_proposal_aggregate_by_id(
        self, proposal_id: UUID
    ) -> ProposalAggregateOutDTO | None:
        return await self.proposal_repository.get_proposal_aggregate_by_id(proposal_id)

    async def list_proposals(self) -> list[ProposalOutDTO]:
        return await self.proposal_repository.list_proposals()

    async def update_proposal(
        self, proposal_id: UUID, payload: ProposalUpdateDTO
    ) -> ProposalAggregateOutDTO | None:
        return await self.proposal_repository.update_proposal(proposal_id, payload)

    async def soft_delete_proposal(self, proposal_id: UUID) -> None:
        await self.proposal_repository.soft_delete_proposal(proposal_id)

    async def create_proposal_with_relations(
        self, payload: ProposalAggregateCreateDTO
    ) -> ProposalAggregateOutDTO:
        return await self.proposal_repository.create_proposal_with_relations(payload)

    async def create_proposal(self, proposal: CreatedProposalDTO) -> CreatedProposalDTO:
        return await self.proposal_repository.create_proposal(proposal)

    async def create_proposal_account(
        self, proposal_account: CreatedProposalAccountDTO
    ) -> CreatedProposalAccountDTO:
        return await self.proposal_repository.create_proposal_account(proposal_account)

    async def create_proposal_document(
        self, proposal_document: CreatedProposalDocumentDTO
    ) -> CreatedProposalDocumentDTO:
        return await self.proposal_repository.create_proposal_document(
            proposal_document
        )

    async def create_proposal_loan(
        self, proposal_loan: CreatedProposalLoanDTO
    ) -> CreatedProposalLoanDTO:
        return await self.proposal_repository.create_proposal_loan(proposal_loan)
