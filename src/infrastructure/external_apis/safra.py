import httpx

from src.core.config.settings import get_settings
from src.core.exceptions.custom import InfrastructureException
from src.infrastructure.external_apis.api_base_client import ApiBaseClient

settings = get_settings()

URL_BANKERS = '/api/v1/Banco'
URL_TOKEN = '/api/v1/Token'


class SafraApi(ApiBaseClient):
    def __init__(self) -> None:
        super().__init__(
            name='Safra',
            base_url=settings.API_SAFRA_BASE_URL,
            timeout=settings.API_SAFRA_TIMEOUT,
            default_headers=settings.API_SAFRA_DEFAULT_HEADERS,
        )

    async def get_token(self) -> httpx.Response:
        return await self.request({
            'method': 'POST',
            'url': URL_TOKEN,
            'json': {
                'username': settings.API_SAFRA_USERNAME,
                'password': settings.API_SAFRA_PASSWORD,
            },
        })

    def _access_token_from(self, token_response: httpx.Response) -> str:
        payload = token_response.json()
        if isinstance(payload, dict):
            token = payload.get('token')
            if isinstance(token, str) and token:
                return token
        raise InfrastructureException(
            'Resposta do token Safra inválida: campo "token" ausente ou vazio.'
        )

    async def get_bankers(self) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'GET',
            'url': URL_BANKERS,
            'headers': {'Authorization': f'Bearer {access_token}'},
        })
