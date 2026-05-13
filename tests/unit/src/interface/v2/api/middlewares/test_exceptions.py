import json
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from src.core.exceptions.custom import (
    DomainException,
    InfrastructureException,
    MultipleException,
)
from src.interface.api.v2.middlewares.exceptions import (
    custom_exception_handler,
    request_validation_exception_handler,
    sanitize_for_json,
)
from starlette import status

STATUS_CODE_422 = 422


@pytest.mark.unit
class TestCustomExceptionHandler:
    @pytest.fixture
    def request_mock(self):
        return MagicMock(spec=Request)

    async def test_domain_exception_returns_400(self, request_mock):
        status_code = 400
        exc = DomainException('Erro de domínio')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        body = response.body.decode()
        assert 'DOMAIN_ERROR' in body or 'message' in body

    async def test_infrastructure_exception_returns_500(self, request_mock):
        status_code = 500
        exc = InfrastructureException('Erro interno')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        body = response.body.decode()
        assert 'INTERNAL_ERROR' in body or 'message' in body

    async def test_multiple_exception_returns_errors_list(self, request_mock):
        status_code = 400
        err1 = DomainException('Erro 1')
        err2 = DomainException('Erro 2')
        exc = MultipleException(err1, err2)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        content = json.loads(response.body.decode())
        assert isinstance(content, list)
        assert len(content) >= 1

    async def test_generic_exception_returns_500(self, request_mock):
        status_code = 500
        exc = ValueError('Qualquer erro')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code

    async def test_httpx_http_status_error_returns_502_with_upstream_body(
        self, request_mock
    ):
        req = httpx.Request('GET', 'http://upstream.example/api')
        resp = httpx.Response(401, request=req, content=b'{"detail":"nope"}')
        exc = httpx.HTTPStatusError('bad', request=req, response=resp)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = json.loads(response.body.decode())
        assert body['code'] == 'UPSTREAM_HTTP_ERROR'
        assert body['upstream_status'] == status.HTTP_401_UNAUTHORIZED
        assert 'nope' in body['upstream_body'] or body.get('message') == 'nope'
        assert body['message'] == 'nope'

    async def test_httpx_400_json_mensagem_returns_400_and_bank_message(
        self, request_mock
    ):
        payload = (
            '{"mensagem":"Não foi possível realizar consulta de margem, '
            'verifique os dados informados."}'
        )
        req = httpx.Request(
            'POST',
            'http://upstream.example/api/v1/ConsultaMargem/Bpo',
        )
        resp = httpx.Response(
            400,
            request=req,
            content=payload.encode(),
        )
        exc = httpx.HTTPStatusError('bad request', request=req, response=resp)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.body.decode())
        assert body['code'] == 'UPSTREAM_HTTP_ERROR'
        assert body['upstream_status'] == status.HTTP_400_BAD_REQUEST
        assert body['upstream_message'] == (
            'Não foi possível realizar consulta de margem, '
            'verifique os dados informados.'
        )
        assert body['message'] == body['upstream_message']
        assert 'upstream_json' in body
        assert body['upstream_json']['mensagem'] == body['upstream_message']

    async def test_httpx_non_json_body_uses_generic_message(self, request_mock):
        req = httpx.Request('GET', 'http://upstream.example/api')
        resp = httpx.Response(
            503,
            request=req,
            content=b'upstream down',
        )
        exc = httpx.HTTPStatusError('bad', request=req, response=resp)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = json.loads(response.body.decode())
        assert 'Chamada HTTP a serviço externo falhou' in body['message']
        assert body['upstream_body'] == 'upstream down'

    async def test_httpx_invalid_json_body(self, request_mock):
        req = httpx.Request('GET', 'http://upstream.example/api')
        resp = httpx.Response(400, request=req, content=b'not-json-{')
        exc = httpx.HTTPStatusError('bad', request=req, response=resp)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.body.decode())
        assert 'Chamada HTTP a serviço externo falhou' in body['message']

    async def test_httpx_json_without_known_message_field(self, request_mock):
        req = httpx.Request('POST', 'http://upstream.example/api')
        resp = httpx.Response(400, request=req, content=b'{}')
        exc = httpx.HTTPStatusError('bad', request=req, response=resp)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = json.loads(response.body.decode())
        assert 'Chamada HTTP a serviço externo falhou' in body['message']
        assert body['upstream_json'] == {}


@pytest.mark.unit
class TestRequestValidationExceptionHandler:
    @pytest.fixture
    def request_mock(self):
        return MagicMock(spec=Request)

    async def test_request_validation_exception_handler_returns_422_and_sanitizes_body(
        self, request_mock
    ):
        exc = RequestValidationError(
            [{'loc': ('body',), 'msg': 'Invalid', 'type': 'value_error'}],
            body=b'\x89PNG\r\n\x1a\n' + b'\x00' * 10,
        )
        response = await request_validation_exception_handler(request_mock, exc)

        assert response.status_code == STATUS_CODE_422
        content = json.loads(response.body.decode())
        assert content['code'] == 'VALIDATION_ERROR'
        assert 'errors' in content

    async def test_sanitize_for_json_bytes(self):
        out = sanitize_for_json({'body': b'\x89PNG\r\n\x1a\n'})
        assert isinstance(out['body'], str)
        assert out['body'].startswith('<bytes:')
