from abc import ABC, abstractmethod
from typing import List

from src.domain.dtos.safra import BankerResponse, TokenResponse


class SafraRepository(ABC):
    @abstractmethod
    async def get_token(self) -> TokenResponse: ...

    @abstractmethod
    async def get_bankers(self) -> List[BankerResponse]: ...
