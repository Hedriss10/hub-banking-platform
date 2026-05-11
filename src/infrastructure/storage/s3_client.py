from __future__ import annotations

import logging
import mimetypes
from dataclasses import dataclass
from uuid import UUID, uuid4

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
)
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from src.core.config.settings import get_settings
from src.core.exceptions.custom import InfrastructureException

MAX_EXTENSION_LEN = 10

logger = logging.getLogger(__name__)


def _split_csv(value: str) -> set[str]:
    return {v.strip() for v in value.split(',') if v.strip()}


def _guess_extension(filename: str | None, content_type: str | None) -> str:
    if filename and '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[-1].lower()
        if len(ext) <= MAX_EXTENSION_LEN:
            return ext
    if content_type:
        ext = mimetypes.guess_extension(content_type) or ''
        if ext:
            return ext
    return ''


def _build_public_url(*, bucket: str, region: str, key: str, base_url: str) -> str:
    if base_url:
        return f'{base_url.rstrip("/")}/{key.lstrip("/")}'
    if region == 'us-east-1':
        return f'https://{bucket}.s3.amazonaws.com/{key}'
    return f'https://{bucket}.s3.{region}.amazonaws.com/{key}'


@dataclass(frozen=True, slots=True)
class UploadResult:
    url: str
    key: str
    content_type: str
    size_bytes: int


class InvalidFileTypeException(InfrastructureException):
    status_code = 400
    code = 'INVALID_FILE_TYPE'


class FileTooLargeException(InfrastructureException):
    status_code = 413
    code = 'FILE_TOO_LARGE'


class UploadFailedException(InfrastructureException):
    code = 'UPLOAD_FAILED'


class TooManyFilesException(InfrastructureException):
    status_code = 400
    code = 'TOO_MANY_FILES'


class S3Storage:
    def __init__(self, client: BaseClient):
        self._client = client

    @staticmethod
    def from_settings() -> S3Storage:
        settings = get_settings()

        kwargs: dict[str, object] = {
            'region_name': settings.AWS_REGION,
            'config': Config(s3={'addressing_style': settings.AWS_S3_ADDRESSING_STYLE}),
        }

        if settings.AWS_S3_ENDPOINT_URL:
            kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
            kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY

        client = boto3.client('s3', **kwargs)
        return S3Storage(client=client)

    async def _put_object(
        self,
        *,
        key: str,
        body: bytes,
        content_type: str,
    ) -> None:
        settings = get_settings()

        if not settings.AWS_S3_BUCKET_NAME:
            raise UploadFailedException('Bucket não configurado')

        extra_args: dict[str, str] = {'ContentType': content_type}
        if settings.AWS_S3_PUBLIC_READ:
            extra_args['ACL'] = 'public-read'

        try:
            await run_in_threadpool(
                self._client.put_object,
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=key,
                Body=body,
                **extra_args,
            )
        except (NoCredentialsError, PartialCredentialsError) as error:
            logger.exception(
                'S3 upload failed: missing credentials',
                extra={
                    'bucket': settings.AWS_S3_BUCKET_NAME,
                    'region': settings.AWS_REGION,
                    'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
                },
            )
            raise UploadFailedException('Credenciais AWS não configuradas') from error
        except EndpointConnectionError as error:
            logger.exception(
                'S3 upload failed: endpoint connection error',
                extra={
                    'bucket': settings.AWS_S3_BUCKET_NAME,
                    'region': settings.AWS_REGION,
                    'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
                },
            )
            raise UploadFailedException('Falha ao conectar ao S3') from error
        except ClientError as error:
            logger.exception(
                'S3 upload failed: client error',
                extra={
                    'bucket': settings.AWS_S3_BUCKET_NAME,
                    'region': settings.AWS_REGION,
                    'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
                    'error_code': (error.response or {}).get('Error', {}).get('Code'),
                },
            )
            message = 'Erro ao enviar arquivo'
            if settings.DEBUG:
                err_code = (error.response or {}).get('Error', {}).get('Code')
                err_msg = (error.response or {}).get('Error', {}).get('Message')
                message = (
                    f'{message}: {err_code or "ClientError"} - {err_msg or str(error)}'
                )
            raise UploadFailedException(message) from error
        except BotoCoreError as error:
            logger.exception(
                'S3 upload failed: botocore error',
                extra={
                    'bucket': settings.AWS_S3_BUCKET_NAME,
                    'region': settings.AWS_REGION,
                    'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
                },
            )
            message = 'Erro ao enviar arquivo'
            if settings.DEBUG:
                message = f'{message}: {type(error).__name__} - {error}'
            raise UploadFailedException(message) from error
        except Exception as error:  # pragma: no cover (driver-specific)
            logger.exception(
                'S3 upload failed: unexpected error',
                extra={
                    'bucket': settings.AWS_S3_BUCKET_NAME,
                    'region': settings.AWS_REGION,
                    'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
                },
            )
            message = 'Erro ao enviar arquivo'
            if settings.DEBUG:
                message = f'{message}: {type(error).__name__} - {error}'
            raise UploadFailedException(message) from error

    async def _upload_one(
        self,
        *,
        file: UploadFile,
        allowed_content_types: set[str],
        max_bytes: int,
        key_prefix: str,
    ) -> UploadResult:
        settings = get_settings()

        content_type = (file.content_type or '').lower()
        if not content_type or content_type not in allowed_content_types:
            raise InvalidFileTypeException('Tipo de arquivo inválido')

        data = await file.read()
        size_bytes = len(data)
        if size_bytes > max_bytes:
            raise FileTooLargeException('Arquivo muito grande')

        ext = _guess_extension(file.filename, content_type)
        prefix = key_prefix.rstrip('/') + '/'
        key = f'{prefix}{uuid4().hex}{ext}'

        await self._put_object(key=key, body=data, content_type=content_type)

        url = _build_public_url(
            bucket=settings.AWS_S3_BUCKET_NAME,
            region=settings.AWS_REGION,
            key=key,
            base_url=settings.AWS_S3_PUBLIC_BASE_URL,
        )
        return UploadResult(
            url=url,
            key=key,
            content_type=content_type,
            size_bytes=size_bytes,
        )

    async def _upload_company_image(
        self,
        *,
        file: UploadFile,
        company_id: UUID,
        folder: str,
    ) -> UploadResult:
        settings = get_settings()
        allowed = _split_csv(settings.S3_ALLOWED_IMAGE_CONTENT_TYPES)
        max_bytes = settings.S3_UPLOAD_MAX_SIZE_MB * 1024 * 1024
        key_prefix = f'companies/{company_id}/{folder}'
        return await self._upload_one(
            file=file,
            allowed_content_types=allowed,
            max_bytes=max_bytes,
            key_prefix=key_prefix,
        )

    async def upload_product_image(
        self,
        *,
        file: UploadFile,
        company_id: UUID,
    ) -> UploadResult:
        return await self._upload_company_image(
            file=file,
            company_id=company_id,
            folder='products',
        )

    async def upload_service_image(
        self,
        *,
        file: UploadFile,
        company_id: UUID,
    ) -> UploadResult:
        return await self._upload_company_image(
            file=file,
            company_id=company_id,
            folder='services',
        )

    async def upload_proposal_document(
        self,
        *,
        file: UploadFile,
        scope_id: UUID,
    ) -> UploadResult:
        settings = get_settings()
        allowed = _split_csv(settings.S3_ALLOWED_PROPOSAL_CONTENT_TYPES)
        max_bytes = settings.S3_PROPOSAL_UPLOAD_MAX_SIZE_MB * 1024 * 1024
        key_prefix = f'proposals/staging/{scope_id}/documents'
        return await self._upload_one(
            file=file,
            allowed_content_types=allowed,
            max_bytes=max_bytes,
            key_prefix=key_prefix,
        )

    async def upload_proposal_documents(
        self,
        *,
        files: list[UploadFile],
        scope_id: UUID,
    ) -> list[UploadResult]:
        settings = get_settings()
        if len(files) > settings.S3_PROPOSAL_UPLOAD_MAX_FILES:
            raise TooManyFilesException(
                f'No máximo {settings.S3_PROPOSAL_UPLOAD_MAX_FILES} arquivos por envio'
            )
        results: list[UploadResult] = []
        for upload in files:
            results.append(
                await self.upload_proposal_document(file=upload, scope_id=scope_id)
            )
        return results
