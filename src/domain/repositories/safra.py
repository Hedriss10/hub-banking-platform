from abc import ABC, abstractmethod
from typing import List

from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
from src.domain.dtos.safra_tables import SafraTablesDto


class SafraRepository(ABC):
    @abstractmethod
    async def get_token(self) -> TokenResponse: ...

    @abstractmethod
    async def get_bankers(self) -> List[BankerResponse]: ...

    @abstractmethod
    async def get_margem_bpo(
        self, margem_bpo_dto: MargemBpoDto
    ) -> MargemBpoOutputDto: ...

    @abstractmethod
    async def get_financial_agreements(self) -> List[FinancialAgreementResponse]: ...

    @abstractmethod
    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]: ...

    @abstractmethod
    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]: ...

    @abstractmethod
    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto: ...
