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
from src.domain.exceptions.proposal import ProposalNotFoundException
from src.domain.service.proposal import ProposalService


class ProposalUseCase:
    def __init__(self, proposal_service: ProposalService):
        self.proposal_service = proposal_service

    async def get_proposal_aggregate(
        self, proposal_id: UUID
    ) -> ProposalAggregateOutDTO:
        proposal = await self.proposal_service.get_proposal_aggregate_by_id(proposal_id)
        if proposal is None:
            raise ProposalNotFoundException(
                message=f'Proposta {proposal_id} não encontrada',
            )
        return proposal

    async def list_proposals(self) -> list[ProposalOutDTO]:
        return await self.proposal_service.list_proposals()

    async def update_proposal(
        self, proposal_id: UUID, payload: ProposalUpdateDTO
    ) -> ProposalAggregateOutDTO:
        existing = await self.proposal_service.get_proposal_aggregate_by_id(
            proposal_id,
        )
        if existing is None:
            raise ProposalNotFoundException(
                message=f'Proposta {proposal_id} não encontrada',
            )
        updated = await self.proposal_service.update_proposal(proposal_id, payload)
        if updated is None:
            raise ProposalNotFoundException(
                message=f'Proposta {proposal_id} não encontrada',
            )
        return updated

    async def delete_proposal(self, proposal_id: UUID) -> None:
        existing = await self.proposal_service.get_proposal_aggregate_by_id(
            proposal_id,
        )
        if existing is None:
            raise ProposalNotFoundException(
                message=f'Proposta {proposal_id} não encontrada',
            )
        await self.proposal_service.soft_delete_proposal(proposal_id)

    async def create_proposal_with_relations(
        self, payload: ProposalAggregateCreateDTO
    ) -> ProposalAggregateOutDTO:
        return await self.proposal_service.create_proposal_with_relations(payload)

    async def create_proposal(self, proposal: CreatedProposalDTO) -> CreatedProposalDTO:
        return await self.proposal_service.create_proposal(proposal)

    async def create_proposal_account(
        self, proposal_account: CreatedProposalAccountDTO
    ) -> CreatedProposalAccountDTO:
        return await self.proposal_service.create_proposal_account(proposal_account)

    async def create_proposal_document(
        self, proposal_document: CreatedProposalDocumentDTO
    ) -> CreatedProposalDocumentDTO:
        return await self.proposal_service.create_proposal_document(proposal_document)

    async def create_proposal_loan(
        self, proposal_loan: CreatedProposalLoanDTO
    ) -> CreatedProposalLoanDTO:
        return await self.proposal_service.create_proposal_loan(proposal_loan)
