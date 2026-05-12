from typing import List

from src.domain.dtos.safra import BankerResponse, TokenResponse
from src.domain.repositories.safra import SafraRepository
from src.infrastructure.external_apis.safra import SafraApi
from src.infrastructure.repositories.helpers.serializer_json import _json_to_banker_rows


class SafraExternalRepository(SafraRepository):
    def __init__(self) -> None:
        self.api = SafraApi()

    async def get_token(self) -> TokenResponse:
        response = await self.api.get_token()
        return TokenResponse.model_validate(response.json())

    async def get_bankers(self) -> List[BankerResponse]:
        response = await self.api.get_bankers()
        rows = _json_to_banker_rows(response.json())
        return [BankerResponse.model_validate(row) for row in rows]
