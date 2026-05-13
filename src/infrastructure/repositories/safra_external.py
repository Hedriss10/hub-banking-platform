from typing import List

from src.core.config.settings import get_settings
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.repositories.safra import SafraRepository
from src.infrastructure.external_apis.safra import SafraApi
from src.infrastructure.repositories.helpers.serializer_json import _json_to_banker_rows
from src.infrastructure.seed.emulator_safra import try_resolve_margin_bpo_demo_request


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

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> MargemBpoOutputDto:
        settings = get_settings()
        emulator_on = settings.DEBUG or settings.API_SAFRA_MARGIN_RESPONSE_EMULATOR
        if emulator_on:
            demo = try_resolve_margin_bpo_demo_request(margem_bpo_dto)
            if demo is not None:
                return demo
        response = await self.api.get_margem_bpo(margem_bpo_dto)
        return MargemBpoOutputDto.model_validate(response.json())
