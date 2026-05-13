from http import HTTPStatus
from unittest.mock import patch

import httpx
import pytest
from src.infrastructure.external_apis.api_base_client import (
    ApiBaseClient,
)

pytestmark = pytest.mark.unit


class _FakeAsyncClient:
    def __init__(self, response=None, exc=None, **kwargs):
        self._response = response
        self._exc = exc
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def request(self, method, url, json=None):
        if self._exc is not None:
            raise self._exc
        return self._response


def _ok_response() -> httpx.Response:
    req = httpx.Request('GET', 'http://example.com/')
    return httpx.Response(200, request=req, json={'ok': True})


@pytest.fixture
def api_client() -> ApiBaseClient:
    return ApiBaseClient(
        name='X',
        base_url='http://example.com',
        timeout=3.0,
        default_headers={'X-Default': '1'},
    )


@pytest.mark.asyncio
async def test_request_success(api_client: ApiBaseClient) -> None:
    ok = _ok_response()
    with patch('httpx.AsyncClient', return_value=_FakeAsyncClient(ok)):
        resp = await api_client.request({
            'method': 'GET',
            'url': '/path',
            'headers': {'Y': '2'},
            'json': {'a': 1},
        })
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {'ok': True}


@pytest.mark.asyncio
async def test_request_skip_raise_for_status(api_client: ApiBaseClient) -> None:
    req = httpx.Request('GET', 'http://example.com/bad')
    err_body = httpx.Response(500, request=req, content=b'no')
    with patch('httpx.AsyncClient', return_value=_FakeAsyncClient(err_body)):
        resp = await api_client.request({
            'method': 'GET',
            'url': '/bad',
            'raise_for_status': False,
        })
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_request_http_status_error(api_client: ApiBaseClient) -> None:
    req = httpx.Request('GET', 'http://example.com/e')
    bad = httpx.Response(503, request=req, content=b'err')
    with patch('httpx.AsyncClient', return_value=_FakeAsyncClient(bad)):
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await api_client.request({'method': 'GET', 'url': '/e'})
    assert 'HTTP error when calling X' in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_timeout(api_client: ApiBaseClient) -> None:
    with patch(
        'httpx.AsyncClient',
        return_value=_FakeAsyncClient(exc=httpx.TimeoutException('t')),
    ):
        with pytest.raises(httpx.TimeoutException) as exc_info:
            await api_client.request({'method': 'GET', 'url': '/t'})
    assert 'Request to X timed out' in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_connect_error(api_client: ApiBaseClient) -> None:
    with patch(
        'httpx.AsyncClient',
        return_value=_FakeAsyncClient(exc=httpx.ConnectError('c')),
    ):
        with pytest.raises(httpx.ConnectError) as exc_info:
            await api_client.request({'method': 'GET', 'url': '/c'})
    assert 'Connection to X failed' in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_generic_request_error(api_client: ApiBaseClient) -> None:
    with patch(
        'httpx.AsyncClient',
        return_value=_FakeAsyncClient(exc=httpx.RequestError('r')),
    ):
        with pytest.raises(httpx.RequestError) as exc_info:
            await api_client.request({'method': 'GET', 'url': '/r'})
    assert 'HTTP error when calling X' in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_unknown_exception(api_client: ApiBaseClient) -> None:
    with patch(
        'httpx.AsyncClient',
        return_value=_FakeAsyncClient(exc=ValueError('boom')),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await api_client.request({'method': 'GET', 'url': '/x'})
    assert 'Unknown error when calling X' in str(exc_info.value)


def test_normalize_base_url_via_client() -> None:
    assert (
        ApiBaseClient(name='T', base_url='api.exemplo.br').base_url
        == 'https://api.exemplo.br'
    )
    assert (
        ApiBaseClient(name='T', base_url='  https://api.exemplo.br/').base_url
        == 'https://api.exemplo.br'
    )
    assert (
        ApiBaseClient(name='T', base_url='http://localhost:8080/').base_url
        == 'http://localhost:8080'
    )
    assert ApiBaseClient(name='T', base_url='   ').base_url == ''
