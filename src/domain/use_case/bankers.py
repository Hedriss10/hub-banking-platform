from typing import List
from uuid import UUID

from src.domain.dtos.bankers import BankerCreateDto, BankerOutDto, BankerUpdateDto
from src.domain.exceptions.bankers import BankerNotFoundException
from src.domain.service.bankers import BankersService


class BankersUseCase:
    def __init__(self, bankers_service: BankersService):
        self.bankers_service = bankers_service

    async def list_bankers(self) -> List[BankerOutDto]:
        return await self.bankers_service.list_bankers()

    async def get_banker(self, banker_id: UUID) -> BankerOutDto:
        banker = await self.bankers_service.get_banker(banker_id)
        if not banker:
            raise BankerNotFoundException(
                message=f'Banker with id {banker_id} not found'
            )
        return banker

    async def create_banker(self, banker: BankerCreateDto) -> BankerOutDto:
        return await self.bankers_service.create_banker(banker)

    async def update_banker(
        self, banker_id: UUID, data: BankerUpdateDto
    ) -> BankerOutDto:
        existing_banker = await self.bankers_service.get_banker(banker_id)
        if not existing_banker:
            raise BankerNotFoundException(
                message=f'Banker with id {banker_id} not found'
            )
        updated = await self.bankers_service.update_banker(banker_id, data)
        if not updated:
            raise BankerNotFoundException(
                message=f'Banker with id {banker_id} not found'
            )
        return updated

    async def delete_banker(self, banker_id: UUID) -> None:
        banker = await self.bankers_service.get_banker(banker_id)
        if not banker:
            raise BankerNotFoundException(
                message=f'Banker with id {banker_id} not found'
            )
        return await self.bankers_service.delete_banker(banker_id)
