from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.service.proposal import ProposalService


class ProposalUseCase:
    def __init__(self, proposal_service: ProposalService):
        self.proposal_service = proposal_service

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
