from typing import List

from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.domain.service.safra import SafraService


class SafraUseCase:
    def __init__(self, safra_service: SafraService) -> None:
        self._safra_service = safra_service

    async def get_token(self) -> TokenResponse:
        return await self._safra_service.get_token()

    async def get_bankers(self) -> List[BankerResponse]:
        return await self._safra_service.get_bankers()
