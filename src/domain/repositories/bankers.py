from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.bankers import BankerCreateDto, BankerOutDto, BankerUpdateDto


class BankersRepository(ABC):
    @abstractmethod
    async def list_bankers(self) -> List[BankerOutDto]: ...

    @abstractmethod
    async def get_banker(self, banker_id: UUID) -> Optional[BankerOutDto]: ...

    @abstractmethod
    async def create_banker(self, banker: BankerCreateDto) -> BankerOutDto: ...

    @abstractmethod
    async def update_banker(
        self, banker_id: UUID, banker: BankerUpdateDto
    ) -> Optional[BankerOutDto]: ...

    @abstractmethod
    async def delete_banker(self, banker_id: UUID) -> None: ...
