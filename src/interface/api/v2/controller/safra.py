from typing import List

from src.domain.dtos.safra import BankerResponse, MargemBpoDto, TokenResponse
from src.domain.use_case.safra import SafraUseCase
from src.interface.api.v2.schemas.safra import (
    BankerOutSchema,
    MargemBpoInSchema,
    MargemBpoOutSchema,
    TokenOutSchema,
)


def _token_to_schema(dto: TokenResponse) -> TokenOutSchema:
    return TokenOutSchema.model_validate(dto.model_dump(mode='json'))


def _banker_to_schema(dto: BankerResponse) -> BankerOutSchema:
    return BankerOutSchema.model_validate(dto.model_dump(mode='json'))


class SafraController:
    def __init__(self, safra_use_case: SafraUseCase) -> None:
        self._safra_use_case = safra_use_case

    async def get_token(self) -> TokenOutSchema:
        dto = await self._safra_use_case.get_token()
        return _token_to_schema(dto)

    async def list_banks(self) -> List[BankerOutSchema]:
        items = await self._safra_use_case.get_bankers()
        return [_banker_to_schema(row) for row in items]

    async def consult_margem_bpo(self, body: MargemBpoInSchema) -> MargemBpoOutSchema:
        dto = MargemBpoDto.model_validate(body.model_dump())
        out = await self._safra_use_case.get_margem_bpo(dto)
        return MargemBpoOutSchema.model_validate(out.model_dump(mode='json'))
