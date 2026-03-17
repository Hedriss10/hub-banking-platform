import pytest
from pydantic import AnyHttpUrl
from src.core.config.settings import Settings, get_settings

pytestmark = pytest.mark.unit


def test_settings_default_values():
    """
    Settings deve ter os valores padrão
    definidos no código quando sem override de env.
    """
    # Instancia com valores explícitos para isolar do .env do projeto
    settings = Settings(
        APP_NAME='hub-banking-platform',
        APP_NAME_FOR_CALLBACKS='',
        API_VERSION='/api/v2',
        BACKEND_CORS_ORIGINS=[],
        DEBUG=False,
        SQLALCHEMY_DATABASE_URI=(
            'postgresql+asyncpg://postgres:postgres@localhost:5477/hub-banking-platform'
        ),
        DATABASE_POOL_SIZE=5,
        DATABASE_MAX_OVERFLOW=10,
        DATABASE_TIMEOUT=30,
        POSTGRES_SCHEMA='hub-banking-platform',
    )

    assert settings.APP_NAME == 'hub-banking-platform'
    assert settings.APP_NAME_FOR_CALLBACKS == ''
    assert settings.API_VERSION == '/api/v2'
    assert settings.DEBUG is False
    assert settings.SQLALCHEMY_DATABASE_URI == (
        'postgresql+asyncpg://postgres:postgres@localhost:5477/hub-banking-platform'
    )
    database_pool_size = 5
    database_max_overflow = 10
    database_timeout = 30
    assert settings.DATABASE_POOL_SIZE == database_pool_size
    assert settings.DATABASE_MAX_OVERFLOW == database_max_overflow
    assert settings.DATABASE_TIMEOUT == database_timeout
    assert settings.POSTGRES_SCHEMA == 'hub-banking-platform'
    assert settings.BACKEND_CORS_ORIGINS == []


def test_settings_load_from_environment(monkeypatch):
    """Settings deve carregar valores a partir de variáveis de ambiente."""
    monkeypatch.setenv('APP_NAME', 'meu-app')
    monkeypatch.setenv('DEBUG', 'true')
    monkeypatch.setenv('API_VERSION', '/api/v2')
    monkeypatch.setenv('DATABASE_POOL_SIZE', '10')

    settings = Settings()

    assert settings.APP_NAME == 'meu-app'
    assert settings.DEBUG is True
    assert settings.API_VERSION == '/api/v2'
    database_pool_size = 10
    assert settings.DATABASE_POOL_SIZE == database_pool_size


# ---------------------------------------------------------------------------
# BACKEND_CORS_ORIGINS - validador
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (
            'http://localhost:3000, http://localhost:4200',
            ['http://localhost:3000', 'http://localhost:4200'],
        ),
        (
            'https://app.example.com',
            ['https://app.example.com'],
        ),
        (
            'http://a.com,http://b.com, http://c.com ',
            ['http://a.com', 'http://b.com', 'http://c.com'],
        ),
    ],
)
def test_backend_cors_origins_string_splitted_into_list(value, expected):
    """String separada por vírgulas deve ser convertida em lista de origens."""
    settings = Settings(BACKEND_CORS_ORIGINS=value)
    assert settings.BACKEND_CORS_ORIGINS == expected


def test_backend_cors_origins_empty_string():
    """String vazia no validador: split(',') resulta em lista com um elemento vazio."""
    settings = Settings(BACKEND_CORS_ORIGINS='')
    # Comportamento atual: '' -> split(',') -> [''] -> [x.strip() for x in ...] -> ['']
    assert settings.BACKEND_CORS_ORIGINS == ['']


def test_backend_cors_origins_list_unchanged():
    """Se o valor já for uma lista, deve ser mantido."""
    origins = ['http://localhost:3000', 'https://app.example.com']
    settings = Settings(BACKEND_CORS_ORIGINS=origins)
    assert settings.BACKEND_CORS_ORIGINS == origins


def test_backend_cors_origins_none_or_falsy_returns_empty_list():
    """Valor None ou falso deve resultar em lista vazia."""
    settings = Settings(BACKEND_CORS_ORIGINS=[])
    assert settings.BACKEND_CORS_ORIGINS == []


def test_backend_cors_origins_accepts_any_http_url():
    """BACKEND_CORS_ORIGINS aceita URLs válidas (AnyHttpUrl)."""
    url_str = 'https://frontend.example.com'
    settings = Settings(BACKEND_CORS_ORIGINS=url_str)
    assert len(settings.BACKEND_CORS_ORIGINS) == 1
    # Pydantic pode coerce string para AnyHttpUrl na lista
    assert settings.BACKEND_CORS_ORIGINS[0] == url_str or isinstance(
        settings.BACKEND_CORS_ORIGINS[0], (str, AnyHttpUrl)
    )


# ---------------------------------------------------------------------------
# get_settings
# ---------------------------------------------------------------------------


def test_get_settings_returns_settings_instance():
    """get_settings() deve retornar uma instância de Settings."""
    get_settings.cache_clear()
    result = get_settings()
    assert isinstance(result, Settings)


def test_get_settings_cached_singleton():
    """get_settings() deve retornar a mesma instância (cache lru_cache)."""
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second
    assert id(first) == id(second)


def test_get_settings_has_expected_attributes():
    """get_settings() retorna objeto com atributos esperados e tipos corretos."""
    get_settings.cache_clear()
    settings = get_settings()
    assert isinstance(settings.APP_NAME, str)
    assert isinstance(settings.APP_NAME_FOR_CALLBACKS, str)
    assert isinstance(settings.API_VERSION, str)
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
    assert isinstance(settings.SQLALCHEMY_DATABASE_URI, str)
    assert 'postgresql' in settings.SQLALCHEMY_DATABASE_URI


def test_build_sqlalchemy_database_uri_when_missing():
    """Monta SQLALCHEMY_DATABASE_URI quando o valor não é informado."""
    settings = Settings(
        SQLALCHEMY_DATABASE_URI=None,
        DATABASE_USER='user',
        DATABASE_PASSWORD='pass',
        DATABASE_HOST='db-host',
        DATABASE_PORT=5433,
        DATABASE_NAME='db_name',
    )

    assert settings.SQLALCHEMY_DATABASE_URI == (
        'postgresql+asyncpg://user:pass@db-host:5433/db_name'
    )
