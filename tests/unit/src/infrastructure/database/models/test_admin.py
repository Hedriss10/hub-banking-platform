import pytest
from src.infrastructure.database.models.admin import Admin

pytestmark = pytest.mark.unit

RESULTS_EXPECTED = 7


def test_admin_model_has_expected_columns():
    Admin.__table__.columns == [
        'id',
        'created_at',
        'updated_at',
        'is_deleted',
        'email',
        'password',
        'role',
    ]
    assert len(Admin.__table__.columns) == RESULTS_EXPECTED


def test_admin_model_name_is_admins():
    assert Admin.__tablename__ == 'admins'
