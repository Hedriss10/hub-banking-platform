from typing import List

from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.domain.use_case.safra import SafraUseCase
from src.interface.api.v2.schemas.safra import BankerOutSchema, TokenOutSchema


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
