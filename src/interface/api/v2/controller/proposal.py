from typing import List
from uuid import UUID

from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalUpdateDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.use_case.proposal import ProposalUseCase
from src.interface.api.v2.schemas.proposal import (
    ProposalCreateSchema,
    ProposalOutSchema,
    ProposalRecordOutSchema,
    ProposalUpdateSchema,
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

    async def list_proposals(self) -> List[ProposalRecordOutSchema]:
        rows = await self.proposal_use_case.list_proposals()
        return [
            ProposalRecordOutSchema.model_validate(row.model_dump()) for row in rows
        ]

    async def get_proposal(self, proposal_id: UUID) -> ProposalOutSchema:
        out = await self.proposal_use_case.get_proposal_aggregate(proposal_id)
        return ProposalOutSchema.model_validate(out.model_dump())

    async def update_proposal(
        self, proposal_id: UUID, patch: ProposalUpdateSchema
    ) -> ProposalOutSchema:
        dto = ProposalUpdateDTO.model_validate(
            patch.model_dump(exclude_unset=True, exclude_none=True)
        )
        out = await self.proposal_use_case.update_proposal(proposal_id, dto)
        return ProposalOutSchema.model_validate(out.model_dump())

    async def delete_proposal(self, proposal_id: UUID) -> None:
        await self.proposal_use_case.delete_proposal(proposal_id)
