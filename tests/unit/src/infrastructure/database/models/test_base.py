import pytest
from sqlalchemy import inspect
from sqlalchemy.schema import MetaData
from src.infrastructure.database.models.base import BaseModel, BaseModelWithEmployee

pytestmark = pytest.mark.unit


def test_base_model_metadata_configured_from_settings():
    """
    BaseModel deve ter metadata configurada (schema vem de POSTGRES_SCHEMA).
    O valor exato depende do .env; ver test_settings.py para POSTGRES_SCHEMA.
    """
    assert BaseModel.metadata is not None
    assert isinstance(BaseModel.metadata, MetaData)
    # schema pode ser None (se não configurado) ou string com nome do schema
    assert BaseModel.metadata.schema is None or isinstance(
        BaseModel.metadata.schema, str
    )


def test_base_model_tablename_converts_to_snake_case():
    """
    __tablename__ deve converter nome da classe em snake_case.
    Ex: UserAccount -> user_account
    """

    class UserAccount(BaseModel):
        __abstract__ = True

    assert UserAccount.__tablename__ == 'user_account'


def test_base_model_tablename_single_word():
    """Classe com uma única palavra deve retornar em minúsculas."""

    class Product(BaseModel):
        __abstract__ = True

    assert Product.__tablename__ == 'product'


def test_base_model_tablename_multiple_caps():
    """Classe com várias palavras em PascalCase."""

    class BankTransaction(BaseModel):
        __abstract__ = True

    assert BankTransaction.__tablename__ == 'bank_transaction'


def test_base_model_has_expected_columns():
    """BaseModel deve ter id, created_at, updated_at e is_deleted."""

    # Modelo concreto necessário para inspect() (abstract não gera mapper)
    class ConcreteBaseColumns(BaseModel):
        __tablename__ = 'test_base_columns'

    mapper = inspect(ConcreteBaseColumns)
    column_names = [c.key for c in mapper.columns]

    assert 'id' in column_names
    assert 'created_at' in column_names
    assert 'updated_at' in column_names
    assert 'is_deleted' in column_names


def test_base_model_id_is_primary_key():
    """Coluna id deve ser primary key."""

    class ConcreteBasePK(BaseModel):
        __tablename__ = 'test_base_primary_key'

    mapper = inspect(ConcreteBasePK)
    id_column = mapper.primary_key[0]
    assert id_column.name == 'id'


def test_base_model_with_employee_is_abstract():
    """BaseModelWithEmployee deve ser abstrato (não gera tabela)."""
    assert getattr(BaseModelWithEmployee, '__abstract__', False) is True


def test_base_model_with_employee_has_created_by():
    """BaseModelWithEmployee deve ter coluna created_by."""

    class ConcreteEmployeeCreatedBy(BaseModelWithEmployee):
        __tablename__ = 'test_employee_created_by'

    mapper = inspect(ConcreteEmployeeCreatedBy)
    column_names = [c.key for c in mapper.columns]

    assert 'created_by' in column_names


def test_base_model_with_employee_inherits_base_columns():
    """BaseModelWithEmployee deve herdar id, created_at, updated_at, is_deleted."""

    class ConcreteEmployeeInherits(BaseModelWithEmployee):
        __tablename__ = 'test_employee_inherits'

    mapper = inspect(ConcreteEmployeeInherits)
    column_names = [c.key for c in mapper.columns]

    assert 'id' in column_names
    assert 'created_at' in column_names
    assert 'updated_at' in column_names
    assert 'is_deleted' in column_names
    assert 'created_by' in column_names
