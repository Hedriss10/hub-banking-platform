import os
from functools import lru_cache
from typing import Any, ClassVar, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações de ambiente usando pydantic_settings.
    O arquivo .env deve estar na mesma pasta ou ser informado via env_file.
    """

    ENVIRONMENT: ClassVar[str] = os.getenv('ENVIRONMENT', 'production')
    model_config = SettingsConfigDict(
        env_file='.env.test' if ENVIRONMENT == 'test' else '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
    )
    # APP
    APP_NAME: str = 'hub-banking-platform'
    APP_NAME_FOR_CALLBACKS: str = ''
    API_VERSION: str = '2.0.0'

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]] = []

    DEBUG: bool = False

    # Banco de dados
    # Preferencialmente defina `SQLALCHEMY_DATABASE_URI`. Se não for definido,
    # a URI é montada a partir das variáveis abaixo.
    DATABASE_HOST: str = 'localhost'
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = 'postgres'
    DATABASE_PASSWORD: str = 'postgres'
    DATABASE_NAME: str = 'hub-banking-platform'
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_TIMEOUT: int = 30

    # schema
    POSTGRES_SCHEMA: str = 'hub-banking-platform'

    # Auth (JWT)
    JWT_SECRET: str = ''
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_MINUTES: int = 36000

    # S3 / Contabo Object Storage
    AWS_REGION: str = ''
    AWS_S3_BUCKET_NAME: str = ''
    AWS_S3_PUBLIC_BASE_URL: str = ''
    AWS_S3_ENDPOINT_URL: str = ''
    AWS_S3_PUBLIC_READ: bool = False
    AWS_S3_ADDRESSING_STYLE: str = 'path'
    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''
    S3_UPLOAD_MAX_SIZE_MB: int = 5
    S3_ALLOWED_IMAGE_CONTENT_TYPES: str = 'image/jpeg,image/png,image/webp'
    S3_PROPOSAL_UPLOAD_MAX_SIZE_MB: int = 10
    S3_PROPOSAL_UPLOAD_MAX_FILES: int = 20
    S3_ALLOWED_PROPOSAL_CONTENT_TYPES: str = (
        'image/jpeg,image/png,image/webp,application/pdf'
    )

    CONTABO_REGION: str = ''
    CONTABO_S3_BUCKET_NAME: str = ''
    CONTABO_S3_PUBLIC_BASE_URL: str = ''
    CONTABO_S3_ENDPOINT_URL: str = ''
    CONTABO_ACCESS_KEY_ID: str = ''
    CONTABO_SECRET_ACCESS_KEY: str = ''

    # Safra
    API_SAFRA_BASE_URL: str = ''
    API_SAFRA_TIMEOUT: float = 10.0
    API_SAFRA_DEFAULT_HEADERS: dict[str, str] = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    API_SAFRA_USERNAME: str = ''
    API_SAFRA_PASSWORD: str = ''
    # Fallback adicional quando DEBUG=false (ex.: produção só com flag explícita)
    API_SAFRA_MARGIN_RESPONSE_EMULATOR: bool = False

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    def split_origins(cls, value: Any) -> Union[List[str], List[AnyHttpUrl]]:
        """
        Se for uma string separada por vírgulas
        (ex: "http://localhost:3000, http://localhost:4200"),
        converte em lista. Caso não seja, retorna no estado atual.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',')]
        return value or []

    @model_validator(mode='after')
    def build_sqlalchemy_database_uri(self) -> 'Settings':
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f'postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}'
                f'@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}'
            )
        return self

    @model_validator(mode='after')
    def normalize_contabo_s3_settings(self) -> 'Settings':
        if not self.AWS_REGION:
            self.AWS_REGION = self.CONTABO_REGION
        if not self.AWS_S3_BUCKET_NAME:
            self.AWS_S3_BUCKET_NAME = self.CONTABO_S3_BUCKET_NAME
        if not self.AWS_S3_PUBLIC_BASE_URL:
            self.AWS_S3_PUBLIC_BASE_URL = self.CONTABO_S3_PUBLIC_BASE_URL
        if not self.AWS_S3_ENDPOINT_URL:
            self.AWS_S3_ENDPOINT_URL = self.CONTABO_S3_ENDPOINT_URL
        if not self.AWS_ACCESS_KEY_ID:
            self.AWS_ACCESS_KEY_ID = self.CONTABO_ACCESS_KEY_ID
        if not self.AWS_SECRET_ACCESS_KEY:
            self.AWS_SECRET_ACCESS_KEY = self.CONTABO_SECRET_ACCESS_KEY
        return self


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única das configurações (singleton),
    aproveitando cache de functools.lru_cache.
    """
    return Settings()
