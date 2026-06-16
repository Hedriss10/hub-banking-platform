from typing import Optional, Union
from urllib.parse import urlencode

import httpx

from src.core.config.settings import get_settings
from src.core.exceptions.custom import InfrastructureException
from src.domain.dtos.safra import MargemBpoDto
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    CalculationRefinRequestDto,
    CalculationRequestDto,
)
from src.domain.dtos.safra_credit_ligth_house import CreditLighthouseDto
from src.domain.dtos.safra_formalization_link import FormalizationLinkQueryDto
from src.domain.dtos.safra_leads import LeadReturnUploadItemDto
from src.domain.dtos.safra_proposal import ProposalDto
from src.domain.dtos.safra_proposal_attachment import ProposalAttachmentDto
from src.domain.dtos.safra_proposal_tracking import ProposalListQueryDto
from src.infrastructure.external_apis.api_base_client import ApiBaseClient

settings = get_settings()

URL_BANKERS = '/api/v1/Banco'
URL_TOKEN = '/api/v1/Token'
URL_MARGEM_BPO = '/api/v1/ConsultaMargem/Bpo'
URL_FINANCIAL_AGREEMENTS = '/api/v1/Convenio'
URL_OPERATIONAL_GUIDE = '/api/v1/Convenio/RoteiroOperacional'
URL_CREDIT_LIGHTHOUSE = '/api/v1/FarolCredito'
URL_LIST_SAFRA_TABLES = '/api/v1/TabelaJuros'
URL_INTEREST_TABLE_BANDS = '/api/v1/TabelaJuros/Faixas'
URL_CALCULATION_NEW = '/api/v1/Calculo/Novo'
URL_CALCULATION_REFIN = '/api/v1/Calculo/Refin'
URL_CALCULATION_PORTABILITY = '/api/v1/Calculo/Portabilidade'
URL_CALCULATION_PORTABILITY_REFIN = '/api/v1/Calculo/PortabilidadeRefin'
URL_PROPOSALS = '/api/v1/Propostas'
URL_PROPOSAL = '/api/v1/Propostas/Novo'
URL_PROPOSAL_ATTACHMENT = '/api/v1/Propostas'
URL_LEADS = '/api/v1/Lead'
URL_LEADS_DOWNLOAD = '/api/v1/Lead/Download'
URL_LEADS_UPLOAD_RETURN = '/api/v1/Lead/UploadRetorno'
URL_LEADS_UPLOAD_RETURN_FILE = '/api/v1/Lead/UploadArquivoRetorno'
URL_PROPOSAL_FORMALIZATION_LINK = '/api/v1/Propostas/ObterLinkFormalizacao'
URL_PROPOSAL_FLOW = '/api/v1/FluxoProposta'
URL_FORMALIZATION_TRACKING = '/api/v1/AcompanhamentoFormalizacao'
URL_PARADINHA_APPROVE = '/api/v1/ParadinhaCorrespondente/aprova'
URL_PARADINHA_CANCEL = '/api/v1/ParadinhaCorrespondente/cancela'
URL_AGENCIES = '/api/v1/Agencia'
URL_POSITIONS = '/api/v1/Cargo'
URL_EMPLOYMENT_BONDS = '/api/v1/VinculoEmpregaticio'
URL_EMPLOYING_BODIES = '/api/v1/OrgaoEmpregador'
URL_PROFESSIONS = '/api/v1/Profissao'
URL_LEGAL_REGIME = '/api/v1/RegimeJuridico'
URL_EMPLOYEE_SITUATION = '/api/v1/SituacaoEmpregado'
URL_CONTRACTS_REGISTRATION_CPF = '/api/v1/ContratosDadosCadastrais/cpf'
URL_CONTRACTS_REGISTRATION_DATE = '/api/v1/ContratosDadosCadastrais/data'
URL_CONTRACTS_REGISTRATION_PROPOSAL = '/api/v1/ContratosDadosCadastrais/proposta'
URL_CONTRACTS_LOAN_CPF = '/api/v1/ContratosEmprestimo/cpf'
URL_CONTRACTS_LOAN_DATE = '/api/v1/ContratosEmprestimo/data'
URL_CONTRACTS_LOAN_PROPOSAL = '/api/v1/ContratosEmprestimo/proposta'
URL_CONTRACTS_FINANCIAL_CPF = '/api/v1/ContratosFinanceiro/cpf'
URL_CONTRACTS_FINANCIAL_DATE = '/api/v1/ContratosFinanceiro/data'
URL_CONTRACTS_FINANCIAL_PROPOSAL = '/api/v1/ContratosFinanceiro/proposta'
URL_CONTRACTS_STATUS_CPF = '/api/v1/ContratosStatus/cpf'
URL_CONTRACTS_STATUS_DATE = '/api/v1/ContratosStatus/data'
URL_CONTRACTS_STATUS_PROPOSAL = '/api/v1/ContratosStatus/proposta'


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

    async def _access_token(self) -> str:
        token_response = await self.get_token()
        return self._access_token_from(token_response)

    @staticmethod
    def _url_with_query(base_url: str, query: dict[str, object]) -> str:
        filtered = {k: v for k, v in query.items() if v is not None}
        if not filtered:
            return base_url
        return f'{base_url}?{urlencode(filtered)}'

    async def _authenticated_get(self, url: str) -> httpx.Response:
        access_token = await self._access_token()
        return await self.request({
            'method': 'GET',
            'url': url,
            'headers': {'Authorization': f'Bearer {access_token}'},
        })

    async def _authenticated_post(
        self,
        url: str,
        json: Optional[Union[dict, list]] = None,
    ) -> httpx.Response:
        access_token = await self._access_token()
        payload: dict = {
            'method': 'POST',
            'url': url,
            'headers': {'Authorization': f'Bearer {access_token}'},
        }
        if json is not None:
            payload['json'] = json
        return await self.request(payload)

    async def _authenticated_post_multipart(
        self, url: str, files: dict
    ) -> httpx.Response:
        access_token = await self._access_token()
        return await self.request({
            'method': 'POST',
            'url': url,
            'headers': {'Authorization': f'Bearer {access_token}'},
            'files': files,
        })

    async def get_bankers(self) -> httpx.Response:
        return await self._authenticated_get(URL_BANKERS)

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> httpx.Response:
        return await self._authenticated_post(
            URL_MARGEM_BPO,
            json=margem_bpo_dto.model_dump(),
        )

    async def get_financial_agreements(self) -> httpx.Response:
        return await self._authenticated_get(URL_FINANCIAL_AGREEMENTS)

    async def get_operational_guide(self, convenio_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_OPERATIONAL_GUIDE}/{convenio_id}',
        )

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            URL_CREDIT_LIGHTHOUSE,
            json=credit_lighthouse_dto.model_dump(),
        )

    async def list_safra_tables(self, convenio_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_LIST_SAFRA_TABLES}/{convenio_id}',
        )

    async def list_interest_table_bands(self, table_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_INTEREST_TABLE_BANDS}/{table_id}',
        )

    async def post_calculo_novo(
        self, calculation_dto: CalculationRequestDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            URL_CALCULATION_NEW,
            json=calculation_dto.model_dump(mode='json', exclude_none=True),
        )

    async def post_calculo_refin(
        self, calculation_dto: CalculationRefinRequestDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            URL_CALCULATION_REFIN,
            json=calculation_dto.model_dump(mode='json', exclude_none=True),
        )

    async def post_calculo_portabilidade(
        self, calculation_dto: CalculationPortabilityRequestDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            URL_CALCULATION_PORTABILITY,
            json=calculation_dto.model_dump(mode='json', exclude_none=True),
        )

    async def post_calculo_portabilidade_refin(
        self, calculation_dto: CalculationPortRefinRequestDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            URL_CALCULATION_PORTABILITY_REFIN,
            json=calculation_dto.model_dump(mode='json', exclude_none=True),
        )

    async def list_proposals(self, query_dto: ProposalListQueryDto) -> httpx.Response:
        url = self._url_with_query(URL_PROPOSALS, query_dto.to_query())
        return await self._authenticated_get(url)

    async def post_safra_proposal(self, proposal_dto: ProposalDto) -> httpx.Response:
        return await self._authenticated_post(
            URL_PROPOSAL,
            json=proposal_dto.model_dump(),
        )

    async def post_proposal_attachment(
        self, proposal_id: int, attachment_dto: ProposalAttachmentDto
    ) -> httpx.Response:
        return await self._authenticated_post(
            f'{URL_PROPOSAL_ATTACHMENT}/{proposal_id}/DocumentoAnexo',
            json=attachment_dto.model_dump(),
        )

    async def list_leads(self) -> httpx.Response:
        return await self._authenticated_get(URL_LEADS)

    async def download_leads_csv(self) -> httpx.Response:
        return await self._authenticated_get(URL_LEADS_DOWNLOAD)

    async def upload_leads_return(
        self, items: list[LeadReturnUploadItemDto]
    ) -> httpx.Response:
        payload = [item.model_dump(mode='json', exclude_none=True) for item in items]
        return await self._authenticated_post(URL_LEADS_UPLOAD_RETURN, json=payload)

    async def upload_leads_return_file(
        self, file_content: bytes, filename: str
    ) -> httpx.Response:
        return await self._authenticated_post_multipart(
            URL_LEADS_UPLOAD_RETURN_FILE,
            files={'file': (filename, file_content)},
        )

    async def get_proposal_formalization_link(
        self, query_dto: FormalizationLinkQueryDto
    ) -> httpx.Response:
        url = self._url_with_query(
            URL_PROPOSAL_FORMALIZATION_LINK,
            query_dto.model_dump(mode='json', exclude_none=True),
        )
        return await self._authenticated_get(url)

    async def get_proposal_flow(self, proposal_id: int) -> httpx.Response:
        url = self._url_with_query(URL_PROPOSAL_FLOW, {'idProposta': proposal_id})
        return await self._authenticated_get(url)

    async def get_formalization_tracking(self, proposal_id: int) -> httpx.Response:
        url = self._url_with_query(
            URL_FORMALIZATION_TRACKING,
            {'idProposta': proposal_id},
        )
        return await self._authenticated_get(url)

    async def approve_paradinha(self, proposal_id: int) -> httpx.Response:
        return await self._authenticated_post(
            f'{URL_PARADINHA_APPROVE}/{proposal_id}',
        )

    async def cancel_paradinha(self, proposal_id: int) -> httpx.Response:
        return await self._authenticated_post(
            f'{URL_PARADINHA_CANCEL}/{proposal_id}',
        )

    async def list_agencies(self) -> httpx.Response:
        return await self._authenticated_get(URL_AGENCIES)

    async def list_positions(self, profession_id: int) -> httpx.Response:
        return await self._authenticated_get(f'{URL_POSITIONS}/{profession_id}')

    async def list_employment_bonds(self, convenio_id: int) -> httpx.Response:
        return await self._authenticated_get(f'{URL_EMPLOYMENT_BONDS}/{convenio_id}')

    async def get_employing_bodies(self, financial_agreement_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_EMPLOYING_BODIES}/{financial_agreement_id}',
        )

    async def get_professions(self, financial_agreement_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_PROFESSIONS}/{financial_agreement_id}',
        )

    async def get_legal_regime(self, financial_agreement_id: int) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_LEGAL_REGIME}/{financial_agreement_id}',
        )

    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_EMPLOYEE_SITUATION}/{financial_agreement_id}/{legal_regime_id}',
        )

    async def get_contracts_registration_by_cpf(self, cpf: str) -> httpx.Response:
        return await self._authenticated_get(f'{URL_CONTRACTS_REGISTRATION_CPF}/{cpf}')

    async def get_contracts_registration_by_date(
        self, proposal_date: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_REGISTRATION_DATE}/{proposal_date}',
        )

    async def get_contracts_registration_by_proposal(
        self, proposal_number: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_REGISTRATION_PROPOSAL}/{proposal_number}',
        )

    async def get_contracts_loan_by_cpf(self, cpf: str) -> httpx.Response:
        return await self._authenticated_get(f'{URL_CONTRACTS_LOAN_CPF}/{cpf}')

    async def get_contracts_loan_by_date(self, proposal_date: str) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_LOAN_DATE}/{proposal_date}',
        )

    async def get_contracts_loan_by_proposal(
        self, proposal_number: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_LOAN_PROPOSAL}/{proposal_number}',
        )

    async def get_contracts_financial_by_cpf(self, cpf: str) -> httpx.Response:
        return await self._authenticated_get(f'{URL_CONTRACTS_FINANCIAL_CPF}/{cpf}')

    async def get_contracts_financial_by_date(
        self, proposal_date: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_FINANCIAL_DATE}/{proposal_date}',
        )

    async def get_contracts_financial_by_proposal(
        self, proposal_number: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_FINANCIAL_PROPOSAL}/{proposal_number}',
        )

    async def get_contracts_status_by_cpf(self, cpf: str) -> httpx.Response:
        return await self._authenticated_get(f'{URL_CONTRACTS_STATUS_CPF}/{cpf}')

    async def get_contracts_status_by_date(self, proposal_date: str) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_STATUS_DATE}/{proposal_date}',
        )

    async def get_contracts_status_by_proposal(
        self, proposal_number: str
    ) -> httpx.Response:
        return await self._authenticated_get(
            f'{URL_CONTRACTS_STATUS_PROPOSAL}/{proposal_number}',
        )
