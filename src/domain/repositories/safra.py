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
