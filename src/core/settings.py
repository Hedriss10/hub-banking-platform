import os

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Variável de ambiente obrigatória em produção: {name}')
    return value


class Config:
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = True
    DOCS = os.getenv('DOCS_DEV', '/docs')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-only-change-in-production')
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'


class DevelopmentConfig(Config):
    APPLICATION_ROOT = '/dev'
    ENV = 'development'
    PORT = 5002
    DOCS = os.getenv('DOCS_DEV', '/docs')
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', '')


class ProductionConfig(Config):
    APPLICATION_ROOT = '/athenas'
    ENV = 'production'
    PORT = 5002
    DOCS = os.getenv('DOCS', '/docs')
    DEBUG = False
    SECRET_KEY = _require_env('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _require_env('SQLALCHEMY_DATABASE_URI')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env not in config_by_name:
    raise ValueError(
        f'Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}'
    )


def get_settings() -> Config:
    return config_by_name[flask_env]
