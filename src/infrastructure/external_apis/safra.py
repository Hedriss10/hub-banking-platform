import httpx

from src.core.config.settings import get_settings
from src.core.exceptions.custom import InfrastructureException
from src.domain.dtos.safra import MargemBpoDto
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
)
from src.domain.dtos.safra_proposal import ProposalDto
from src.infrastructure.external_apis.api_base_client import ApiBaseClient

settings = get_settings()

URL_BANKERS = '/api/v1/Banco'
URL_TOKEN = '/api/v1/Token'
URL_MARGEM_BPO = '/api/v1/ConsultaMargem/Bpo'
URL_FINANCIAL_AGREEMENTS = '/api/v1/Convenio'
URL_CREDIT_LIGHTHOUSE = '/api/v1/FarolCredito'
URL_LIST_SAFRA_TABLES = '/api/v1/TabelaJuros'
URL_PROPOSAL = '/api/v1/Propostas/Novo'
URL_EMPLOYING_BODIES = '/api/v1/OrgaoEmpregador'


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

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'POST',
            'url': URL_MARGEM_BPO,
            'headers': {'Authorization': f'Bearer {access_token}'},
            'json': margem_bpo_dto.model_dump(),
        })

    async def get_financial_agreements(self) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'GET',
            'url': URL_FINANCIAL_AGREEMENTS,
            'headers': {'Authorization': f'Bearer {access_token}'},
        })

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'POST',
            'url': URL_CREDIT_LIGHTHOUSE,
            'headers': {'Authorization': f'Bearer {access_token}'},
            'json': credit_lighthouse_dto.model_dump(),
        })

    async def list_safra_tables(self, convenio_id: int) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'GET',
            'url': f'{URL_LIST_SAFRA_TABLES}/{convenio_id}',
            'headers': {'Authorization': f'Bearer {access_token}'},
        })

    async def post_safra_proposal(self, proposal_dto: ProposalDto) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'POST',
            'url': URL_PROPOSAL,
            'headers': {'Authorization': f'Bearer {access_token}'},
            'json': proposal_dto.model_dump(),
        })

    async def get_employing_bodies(self, financial_agreement_id: int) -> httpx.Response:
        token_response = await self.get_token()
        access_token = self._access_token_from(token_response)
        return await self.request({
            'method': 'GET',
            'url': f'{URL_EMPLOYING_BODIES}/{financial_agreement_id}',
            'headers': {'Authorization': f'Bearer {access_token}'},
        })
