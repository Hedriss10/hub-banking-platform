import pytest
from src.infrastructure.database.models.loan_operation import LoanOperation

pytestmark = pytest.mark.unit


@pytest.mark.unit
def test_loan_operation_model_tablename():
    assert LoanOperation.__tablename__ == 'loan_operation'


def test_loan_operation_model_has_expected_columns():
    arrange_result = 6
    LoanOperation.__table__.columns == [
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'name',
    ]
    assert len(LoanOperation.__table__.columns) == arrange_result
