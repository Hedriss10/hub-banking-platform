from abc import ABC, abstractmethod

from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO


class IProposalRepository(ABC):
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
