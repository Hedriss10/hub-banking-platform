from typing import List, Optional
from uuid import UUID

from src.domain.dtos.bankers import BankerCreateDto, BankerOutDto, BankerUpdateDto
from src.domain.repositories.bankers import BankersRepository


class BankersService:
    def __init__(self, bankers_repository: BankersRepository):
        self.bankers_repository = bankers_repository

    async def list_bankers(self) -> List[BankerOutDto]:
        return await self.bankers_repository.list_bankers()

    async def get_banker(self, banker_id: UUID) -> Optional[BankerOutDto]:
        return await self.bankers_repository.get_banker(banker_id)

    async def create_banker(self, banker: BankerCreateDto) -> BankerOutDto:
        return await self.bankers_repository.create_banker(banker)

    async def update_banker(
        self, banker_id: UUID, banker: BankerUpdateDto
    ) -> Optional[BankerOutDto]:
        return await self.bankers_repository.update_banker(banker_id, banker)

    async def delete_banker(self, banker_id: UUID) -> None:
        return await self.bankers_repository.delete_banker(banker_id)
