from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import src.infrastructure.storage.s3_client as s3_client_mod
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
)
from fastapi import UploadFile
from src.infrastructure.storage.s3_client import (
    FileTooLargeException,
    InvalidFileTypeException,
    S3Storage,
    TooManyFilesException,
    UploadFailedException,
    _build_public_url,
    _guess_extension,
    _split_csv,
)
from starlette.datastructures import Headers


def _upload_file(
    *,
    filename: str = 'x.jpg',
    body: bytes = b'abc',
    content_type: str = 'image/jpeg',
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(body),
        headers=Headers({'content-type': content_type}),
    )


def _settings(**overrides: object) -> SimpleNamespace:
    base = dict(
        AWS_REGION='sa-east-1',
        AWS_S3_BUCKET_NAME='my-bucket',
        AWS_S3_PUBLIC_BASE_URL='https://cdn.example/base',
        AWS_ACCESS_KEY_ID='k',
        AWS_SECRET_ACCESS_KEY='s',
        AWS_S3_ENDPOINT_URL='https://s3.example',
        AWS_S3_PUBLIC_READ=False,
        AWS_S3_ADDRESSING_STYLE='path',
        S3_ALLOWED_IMAGE_CONTENT_TYPES='image/jpeg,image/png',
        S3_UPLOAD_MAX_SIZE_MB=5,
        S3_ALLOWED_PROPOSAL_CONTENT_TYPES='image/jpeg,application/pdf',
        S3_PROPOSAL_UPLOAD_MAX_SIZE_MB=10,
        S3_PROPOSAL_UPLOAD_MAX_FILES=5,
        DEBUG=False,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


pytestmark = pytest.mark.unit

_EXPECTED_DEFAULT_JPEG_BYTES = 3
_EXPECTED_BATCH_FILES = 2


def test_split_csv_trims_and_skips_empty() -> None:
    assert _split_csv('a, b,') == {'a', 'b'}


def test_guess_extension_from_filename() -> None:
    assert _guess_extension('a.JPG', None) == '.jpg'


def test_guess_extension_long_ignored_uses_mime() -> None:
    long_name = 'file.' + 'x' * 20
    assert _guess_extension(long_name, 'image/png') == '.png'


def test_guess_extension_only_mime() -> None:
    assert _guess_extension(None, 'image/png') == '.png'


def test_guess_extension_empty() -> None:
    assert _guess_extension(None, None) == ''


def test_build_public_url_base_url() -> None:
    u = _build_public_url(
        bucket='b',
        region='x',
        key='k/path',
        base_url='https://host/prefix/',
    )
    assert u == 'https://host/prefix/k/path'


def test_build_public_url_us_east_no_base() -> None:
    u = _build_public_url(
        bucket='b',
        region='us-east-1',
        key='k',
        base_url='',
    )
    assert 'b.s3.amazonaws.com' in u


def test_build_public_url_other_region() -> None:
    u = _build_public_url(bucket='b', region='sa-east-1', key='k', base_url='')
    assert 'sa-east-1' in u


@pytest.mark.asyncio
async def test_upload_one_invalid_type() -> None:
    storage = S3Storage(MagicMock())
    up = _upload_file(content_type='application/zip')
    with pytest.raises(InvalidFileTypeException):
        await storage._upload_one(
            file=up,
            allowed_content_types={'image/jpeg'},
            max_bytes=9999,
            key_prefix='p',
        )


@pytest.mark.asyncio
async def test_upload_one_type_missing() -> None:
    empty = UploadFile(
        filename='a',
        file=BytesIO(b'1'),
        headers=Headers({}),
    )
    storage = S3Storage(MagicMock())
    with pytest.raises(InvalidFileTypeException):
        await storage._upload_one(
            file=empty,
            allowed_content_types={'image/jpeg'},
            max_bytes=9999,
            key_prefix='p',
        )


@pytest.mark.asyncio
async def test_upload_one_too_large() -> None:
    storage = S3Storage(MagicMock())
    up = _upload_file(body=b'x' * 20)
    with pytest.raises(FileTooLargeException):
        await storage._upload_one(
            file=up,
            allowed_content_types={'image/jpeg'},
            max_bytes=5,
            key_prefix='pfx',
        )


@pytest.mark.asyncio
async def test_put_object_bucket_missing() -> None:
    storage = S3Storage(MagicMock())
    empty_bucket_settings = _settings(AWS_S3_BUCKET_NAME='')
    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=empty_bucket_settings,
    ):
        with pytest.raises(UploadFailedException, match='Bucket'):
            await storage._put_object(
                key='k',
                body=b'1',
                content_type='image/jpeg',
            )


@pytest.mark.asyncio
async def test_put_object_success_and_public_read_acl() -> None:
    client = MagicMock()
    storage = S3Storage(client)
    s = _settings(AWS_S3_PUBLIC_READ=True)

    async def run_pool(_fn, *args, **kwargs):
        _fn(*args, **kwargs)

    with patch.object(s3_client_mod, 'get_settings', return_value=s):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=run_pool):
            await storage._put_object(key='k', body=b'bb', content_type='image/jpeg')

    call_kw = client.put_object.call_args.kwargs
    assert call_kw['ACL'] == 'public-read'


@pytest.mark.asyncio
async def test_put_object_no_credentials() -> None:
    storage = S3Storage(MagicMock())

    async def boom(_fn, *_a, **_k):
        raise NoCredentialsError()

    with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException, match='Credenciais'):
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')


@pytest.mark.asyncio
async def test_put_object_endpoint_error() -> None:
    storage = S3Storage(MagicMock())

    async def boom(_fn, *_a, **_k):
        raise EndpointConnectionError(endpoint_url='x')

    with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException, match='conectar'):
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')


@pytest.mark.asyncio
async def test_put_object_client_error_debug_off() -> None:
    storage = S3Storage(MagicMock())
    err = ClientError({'Error': {'Code': 'X', 'Message': 'Y'}}, 'PutObject')
    settings_debug_off = _settings(DEBUG=False)

    async def boom(_fn, *_a, **_k):
        raise err

    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=settings_debug_off,
    ):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException) as exc_info:
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')
            assert 'Erro ao enviar' in str(exc_info.value)


@pytest.mark.asyncio
async def test_put_object_client_error_debug_on() -> None:
    storage = S3Storage(MagicMock())
    err = ClientError({'Error': {'Code': 'NoSuchBucket', 'Message': 'm'}}, 'PutObject')
    settings_debug_on = _settings(DEBUG=True)

    async def boom(_fn, *_a, **_k):
        raise err

    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=settings_debug_on,
    ):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException) as exc_info:
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')
            assert 'NoSuchBucket' in str(exc_info.value)


@pytest.mark.asyncio
async def test_put_object_botocore_error_debug_on() -> None:
    storage = S3Storage(MagicMock())

    settings_debug_on = _settings(DEBUG=True)

    async def boom(_fn, *_a, **_k):
        raise BotoCoreError()

    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=settings_debug_on,
    ):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException) as exc_info:
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')
            assert 'BotoCoreError' in str(exc_info.value)


@pytest.mark.asyncio
async def test_put_object_unexpected_exception_debug_on() -> None:
    storage = S3Storage(MagicMock())

    settings_debug_on = _settings(DEBUG=True)

    async def boom(_fn, *_a, **_k):
        raise ValueError('oops')

    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=settings_debug_on,
    ):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=boom):
            with pytest.raises(UploadFailedException) as exc_info:
                await storage._put_object(key='k', body=b'1', content_type='image/jpeg')
            assert 'ValueError' in str(exc_info.value)


@pytest.mark.asyncio
async def test_full_upload_proposal_document() -> None:
    client = MagicMock()
    storage = S3Storage(client)

    async def run_pool(fn, *args, **kwargs):
        fn(*args, **kwargs)

    with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=run_pool):
            res = await storage.upload_proposal_document(
                file=_upload_file(content_type='application/pdf', filename='a.pdf'),
                scope_id=uuid4(),
            )
    assert res.size_bytes == _EXPECTED_DEFAULT_JPEG_BYTES
    assert 'proposals/staging' in res.key


@pytest.mark.asyncio
async def test_upload_proposal_documents_batch_and_too_many() -> None:
    client = MagicMock()
    storage = S3Storage(client)

    async def run_pool(fn, *args, **kwargs):
        fn(*args, **kwargs)

    sid = uuid4()
    with patch.object(
        s3_client_mod,
        'get_settings',
        return_value=_settings(S3_PROPOSAL_UPLOAD_MAX_FILES=2),
    ):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=run_pool):
            with pytest.raises(TooManyFilesException):
                await storage.upload_proposal_documents(
                    files=[
                        _upload_file(),
                        _upload_file(),
                        _upload_file(),
                    ],
                    scope_id=sid,
                )

    with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=run_pool):
            out = await storage.upload_proposal_documents(
                files=[
                    _upload_file(),
                    _upload_file(
                        filename='b.pdf',
                        content_type='application/pdf',
                    ),
                ],
                scope_id=sid,
            )
    assert len(out) == _EXPECTED_BATCH_FILES


@pytest.mark.asyncio
async def test_upload_product_and_service_image() -> None:
    client = MagicMock()
    storage = S3Storage(client)
    cid = uuid4()

    async def run_pool(fn, *args, **kwargs):
        fn(*args, **kwargs)

    with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
        with patch.object(s3_client_mod, 'run_in_threadpool', side_effect=run_pool):
            p = await storage.upload_product_image(file=_upload_file(), company_id=cid)
            s = await storage.upload_service_image(file=_upload_file(), company_id=cid)
    assert 'products' in p.key
    assert 'services' in s.key


def test_from_settings_calls_boto_client() -> None:
    fake_client = MagicMock()
    with patch(
        'src.infrastructure.storage.s3_client.boto3.client',
        return_value=fake_client,
    ) as mock_client_fn:
        with patch.object(s3_client_mod, 'get_settings', return_value=_settings()):
            st = S3Storage.from_settings()
    assert isinstance(st, S3Storage)
    assert st._client is fake_client
    mock_client_fn.assert_called_once()
