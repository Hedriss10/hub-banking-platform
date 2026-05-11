from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.enum.document import DocumentType
from src.domain.enum.gender import Gender
from src.domain.enum.proposal_loan import ProposalLoanStatus


class ProposalBaseSchema(BaseModel):
    name: str
    document: Optional[DocumentType] = Field(
        default=None,
        description=(
            'Tipo de documento oficial (CPF, RG, CNH…). '
            'Não enviar número aqui — use cpf ou rg_document.'
        ),
    )
    birth_date: Optional[datetime] = None
    financial_agreements_id: UUID
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    cpf: str = Field(..., min_length=11, max_length=20)
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

    model_config = ConfigDict(str_strip_whitespace=True)


class ProposalAccountSchema(BaseModel):
    bank_agency: Optional[str] = None
    pix_key: Optional[str] = None
    account_number: Optional[str] = None
    agency_digit: Optional[str] = None
    agency_operation: Optional[str] = None
    agency_operation_digit: Optional[str] = None
    account_type: Optional[str] = None
    payment_type: Optional[str] = None
    bank_id: Optional[UUID] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ProposalDocumentSchema(BaseModel):
    document_path: str = Field(
        ...,
        description=(
            'URL pública ou key do objeto no bucket (ex.: retorno de POST '
            '/proposals/documents/upload).'
        ),
    )


class ProposalDocumentUploadItemSchema(BaseModel):
    """Resultado de um arquivo enviado ao object storage (Contabo/S3)."""

    url: str
    key: str
    content_type: str
    size_bytes: int


class ProposalDocumentsUploadOutSchema(BaseModel):
    items: list[ProposalDocumentUploadItemSchema]


class ProposalLoanSchema(BaseModel):
    server_password: Optional[str] = None
    registration_number: Optional[str] = None
    dispatch_date: Optional[datetime] = None
    available_margin: Optional[float] = None
    status: Optional[ProposalLoanStatus] = None
    term_start: Optional[int] = None
    term_end: Optional[int] = None
    operation_amount: Optional[Decimal] = None
    finance_table_id: Optional[int] = None
    financial_agreement_id: Optional[UUID] = None
    loan_operation_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ProposalCreateSchema(BaseModel):
    proposal: ProposalBaseSchema
    account: Optional[ProposalAccountSchema] = None
    documents: list[ProposalDocumentSchema] = Field(default_factory=list)
    loans: list[ProposalLoanSchema] = Field(default_factory=list)


class ProposalUpdateSchema(BaseModel):
    """Partial update only for fields of the proposal entity itself."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=30)
    document: Optional[DocumentType] = Field(
        default=None,
        description=(
            'Tipo de documento oficial (CPF, RG, CNH…). '
            'Não enviar número aqui — use cpf ou rg_document.'
        ),
    )
    birth_date: Optional[datetime] = None
    financial_agreements_id: Optional[UUID] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=20)
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


class ProposalRecordOutSchema(ProposalBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID


class ProposalAccountOutSchema(ProposalAccountSchema):
    id: UUID
    proposal_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID


class ProposalDocumentOutSchema(ProposalDocumentSchema):
    id: UUID
    proposal_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID


class ProposalLoanOutSchema(ProposalLoanSchema):
    id: UUID
    proposal_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by: UUID


class ProposalOutSchema(BaseModel):
    proposal: ProposalRecordOutSchema
    account: Optional[ProposalAccountOutSchema] = None
    documents: list[ProposalDocumentOutSchema] = Field(default_factory=list)
    loans: list[ProposalLoanOutSchema] = Field(default_factory=list)
