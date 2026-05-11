from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.dtos.proposal_account import (
    CreatedProposalAccountDTO,
    ProposalAccountOutDTO,
)
from src.domain.dtos.proposal_document import (
    CreatedProposalDocumentDTO,
    ProposalDocumentOutDTO,
)
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO, ProposalLoanOutDTO
from src.domain.enum.document import DocumentType
from src.domain.enum.gender import Gender


class CreatedProposalDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    document: Optional[DocumentType] = None
    birth_date: Optional[datetime] = None
    financial_agreements_id: UUID
    gender: Optional[Gender] = None
    email: Optional[str] = None
    cpf: str
    place_of_birth: Optional[str] = None
    birth_city: Optional[str] = None
    birth_state: Optional[str] = None
    rg_document: Optional[str] = None
    issuing_authority: Optional[str] = None
    issuing_state: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    address_number: Optional[str] = None
    address_complement: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    gross_salary: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None
    work_phone: Optional[str] = None
    notes: Optional[str] = None
    issue_date: Optional[datetime] = None
    created_by: UUID


class ProposalOutDTO(CreatedProposalDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class ProposalUpdateDTO(BaseModel):
    """Atualização parcial da entidade principal da proposta (sem filhos cascata)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    document: Optional[DocumentType] = None
    birth_date: Optional[datetime] = None
    financial_agreements_id: Optional[UUID] = None
    gender: Optional[Gender] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    place_of_birth: Optional[str] = None
    birth_city: Optional[str] = None
    birth_state: Optional[str] = None
    rg_document: Optional[str] = None
    issuing_authority: Optional[str] = None
    issuing_state: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    address_number: Optional[str] = None
    address_complement: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    gross_salary: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None
    work_phone: Optional[str] = None
    notes: Optional[str] = None
    issue_date: Optional[datetime] = None


class ProposalAggregateCreateDTO(BaseModel):
    proposal: CreatedProposalDTO
    account: Optional[CreatedProposalAccountDTO] = None
    documents: list[CreatedProposalDocumentDTO] = Field(default_factory=list)
    loans: list[CreatedProposalLoanDTO] = Field(default_factory=list)


class ProposalAggregateOutDTO(BaseModel):
    proposal: ProposalOutDTO
    account: Optional[ProposalAccountOutDTO] = None
    documents: list[ProposalDocumentOutDTO] = Field(default_factory=list)
    loans: list[ProposalLoanOutDTO] = Field(default_factory=list)
