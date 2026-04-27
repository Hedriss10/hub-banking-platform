import pytest
from src.infrastructure.database.models.bankers import BankersModel
from src.infrastructure.database.models.financial_agreements import (
    FinancialAgreementsModel,
)
from src.infrastructure.database.models.proposal import ProposalModel
from src.infrastructure.database.models.proposal_acount import (
    ProposalPaymentAccountModel,
)
from src.infrastructure.database.models.proposal_document import ProposalDocumentModel
from src.infrastructure.database.models.proposal_loan import ProposalLoanModel
from src.infrastructure.database.models.rooms import RoomsModel

pytestmark = pytest.mark.unit


def _column_names(model):
    return {c.name for c in model.__table__.columns}


def test_bankers_model_tablename():
    assert BankersModel.__tablename__ == 'bankers'


def test_bankers_model_has_expected_columns():
    assert _column_names(BankersModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'name',
    }


def test_financial_agreements_model_tablename():
    assert FinancialAgreementsModel.__tablename__ == 'financial_agreements'


def test_financial_agreements_model_has_expected_columns():
    assert _column_names(FinancialAgreementsModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'name',
        'bankers_id',
    }


def test_proposal_model_tablename():
    assert ProposalModel.__tablename__ == 'proposals'


def test_proposal_model_has_expected_columns():
    assert _column_names(ProposalModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'name',
        'document',
        'birth_date',
        'financial_agreements_id',
        'gender',
        'email',
        'cpf',
        'place_of_birth',
        'birth_city',
        'birth_state',
        'rg_document',
        'issuing_authority',
        'issuing_state',
        'mother_name',
        'father_name',
        'neighborhood',
        'address',
        'address_number',
        'address_complement',
        'city',
        'state',
        'zip_code',
        'gross_salary',
        'net_salary',
        'mobile_phone',
        'home_phone',
        'work_phone',
        'notes',
        'issue_date',
    }


def test_proposal_payment_account_model_tablename():
    assert ProposalPaymentAccountModel.__tablename__ == 'proposal_acounts'


def test_proposal_payment_account_model_has_expected_columns():
    assert _column_names(ProposalPaymentAccountModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'bank_agency',
        'pix_key',
        'account_number',
        'agency_digit',
        'agency_operation',
        'agency_operation_digit',
        'account_type',
        'payment_type',
        'bank_id',
        'proposal_id',
    }


def test_proposal_document_model_tablename():
    assert ProposalDocumentModel.__tablename__ == 'proposal_documents'


def test_proposal_document_model_has_expected_columns():
    assert _column_names(ProposalDocumentModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'proposal_id',
        'document_path',
    }


def test_proposal_loan_model_tablename():
    # Sem __tablename__ explícito: nome derivado de ProposalLoanModel
    assert ProposalLoanModel.__tablename__ == 'proposal_loan_model'


def test_proposal_loan_model_has_expected_columns():
    assert _column_names(ProposalLoanModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'server_password',
        'registration_number',
        'dispatch_date',
        'available_margin',
        'status',
        'term_start',
        'term_end',
        'operation_amount',
        'proposal_id',
        'finance_table_id',
        'financial_agreement_id',
        'loan_operation_id',
    }


def test_rooms_model_tablename():
    assert RoomsModel.__tablename__ == 'rooms'


def test_rooms_model_has_expected_columns():
    assert _column_names(RoomsModel) == {
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'name',
    }
