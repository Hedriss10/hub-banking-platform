from abc import ABC, abstractmethod
from typing import Optional
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


class IProposalRepository(ABC):
    @abstractmethod
    async def get_proposal_aggregate_by_id(
        self, proposal_id: UUID
    ) -> Optional[ProposalAggregateOutDTO]: ...

    @abstractmethod
    async def list_proposals(self) -> list[ProposalOutDTO]: ...

    @abstractmethod
    async def update_proposal(
        self, proposal_id: UUID, payload: ProposalUpdateDTO
    ) -> Optional[ProposalAggregateOutDTO]: ...

    @abstractmethod
    async def soft_delete_proposal(self, proposal_id: UUID) -> None: ...

    @abstractmethod
    async def create_proposal_with_relations(
        self, payload: ProposalAggregateCreateDTO
    ) -> ProposalAggregateOutDTO: ...

    @abstractmethod
    async def create_proposal(
        self, proposal: CreatedProposalDTO
    ) -> CreatedProposalDTO: ...

    @abstractmethod
    async def create_proposal_account(
        self, proposal_account: CreatedProposalAccountDTO
    ) -> CreatedProposalAccountDTO: ...

    @abstractmethod
    async def create_proposal_document(
        self, proposal_document: CreatedProposalDocumentDTO
    ) -> CreatedProposalDocumentDTO: ...

    @abstractmethod
    async def create_proposal_loan(
        self, proposal_loan: CreatedProposalLoanDTO
    ) -> CreatedProposalLoanDTO: ...
