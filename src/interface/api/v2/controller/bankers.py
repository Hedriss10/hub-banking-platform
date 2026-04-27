from typing import List
from uuid import UUID

from src.domain.dtos.bankers import BankerCreateDto, BankerOutDto, BankerUpdateDto
from src.domain.use_case.bankers import BankersUseCase
from src.interface.api.v2.schemas.bankers import (
    BankerCreateSchema,
    BankerOutSchema,
    BankerUpdateSchema,
)


def _banker_out_to_schema(dto: BankerOutDto) -> BankerOutSchema:
    return BankerOutSchema.model_validate(dto.model_dump(mode='json'))


class BankersController:
    def __init__(self, banker_use_case: BankersUseCase):
        self.banker_use_case = banker_use_case

    async def list_bankers(self) -> List[BankerOutSchema]:
        items = await self.banker_use_case.list_bankers()
        return [_banker_out_to_schema(row) for row in items]

    async def get_banker(self, banker_id: UUID) -> BankerOutSchema:
        banker_dto = await self.banker_use_case.get_banker(banker_id)
        return _banker_out_to_schema(banker_dto)

    async def create_banker(
        self, banker: BankerCreateSchema, created_by: UUID
    ) -> BankerOutSchema:
        dto = BankerCreateDto(name=banker.name, created_by=created_by)
        banker_dto = await self.banker_use_case.create_banker(dto)
        return _banker_out_to_schema(banker_dto)

    async def update_banker(
        self, banker_id: UUID, banker: BankerUpdateSchema
    ) -> BankerOutSchema:
        update_dto = BankerUpdateDto.model_validate(banker.model_dump())
        banker_dto = await self.banker_use_case.update_banker(banker_id, update_dto)
        return _banker_out_to_schema(banker_dto)

    async def delete_banker(self, banker_id: UUID) -> None:
        await self.banker_use_case.delete_banker(banker_id)
