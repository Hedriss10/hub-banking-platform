from uuid import UUID

from src.domain.dtos.proposal import CreatedProposalDTO, ProposalAggregateCreateDTO
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.use_case.proposal import ProposalUseCase
from src.interface.api.v2.schemas.proposal import (
    ProposalCreateSchema,
    ProposalOutSchema,
)


class ProposalController:
    def __init__(self, proposal_use_case: ProposalUseCase):
        self.proposal_use_case = proposal_use_case

    async def create_proposal(
        self, proposal: ProposalCreateSchema, created_by: UUID
    ) -> ProposalOutSchema:
        payload = ProposalAggregateCreateDTO(
            proposal=CreatedProposalDTO(
                **proposal.proposal.model_dump(),
                created_by=created_by,
            ),
            account=(
                CreatedProposalAccountDTO(
                    **proposal.account.model_dump(),
                    created_by=created_by,
                    proposal_id=None,
                )
                if proposal.account
                else None
            ),
            documents=[
                CreatedProposalDocumentDTO(
                    **document.model_dump(),
                    created_by=created_by,
                    proposal_id=None,
                )
                for document in proposal.documents
            ],
            loans=[
                CreatedProposalLoanDTO(
                    **loan.model_dump(),
                    created_by=created_by,
                    proposal_id=None,
                )
                for loan in proposal.loans
            ],
        )
        out = await self.proposal_use_case.create_proposal_with_relations(payload)
        return ProposalOutSchema.model_validate(out.model_dump())
