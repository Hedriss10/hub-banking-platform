import pytest
from src.infrastructure.database.models.employee import Employee

pytestmark = pytest.mark.unit

RESULTS_EXPECTED = 10


def test_employee_model_has_expected_columns():
    Employee.__table__.columns == [
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'created_by',
        'first_name',
        'last_name',
        'role',
        'email',
        'document',
        'password',
    ]
    assert len(Employee.__table__.columns) == RESULTS_EXPECTED


def test_employee_model_name_is_employees():
    assert Employee.__tablename__ == 'employees'
