import json
from typing import Union

import httpx
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions.custom import (
    DomainException,
    InfrastructureException,
    MultipleException,
)
from src.core.utils.get_from_sequence import get_from_sequence


def sanitize_for_json(obj: object) -> object:
    """
    Garante que não existam bytes nem exceções na resposta JSON.

    O FastAPI tenta serializar bytes como utf-8 por padrão, o que pode quebrar
    quando o payload é binário (ex.: PNG).

    Os erros do Pydantic podem incluir `ctx.error` ou similares com objeto
    `ValueError`; esses valores não são JSON-serializable sem conversão para str.
    """
    if isinstance(obj, BaseException):
        return str(obj)
    if isinstance(obj, bytes):
        return f'<bytes:{len(obj)}>'
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    return obj


# Compat: testes/uso antigo
_sanitize_for_json = sanitize_for_json


def _upstream_http_error_response_content(
    resp: httpx.Response,
) -> tuple[int, dict[str, object]]:
    """
    Monta corpo e status HTTP de resposta quando um serviço externo retorna erro.
    Tenta extrair mensagem amigável (ex.: campo `mensagem` da API Safra).
    """
    text = (resp.text or '')[:2000]
    parsed: object | None = None
    bank_message: str | None = None

    if text.strip():
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None

    if isinstance(parsed, dict):
        for key in ('mensagem', 'message', 'detail', 'erro'):
            val = parsed.get(key)
            if isinstance(val, str) and val.strip():
                bank_message = val.strip()
                break

    if bank_message:
        message = bank_message
    else:
        message = (
            'Chamada HTTP a serviço externo falhou. '
            'Veja upstream_status e upstream_body (resposta da API remota).'
        )

    upstream_status = resp.status_code
    if upstream_status in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_422_UNPROCESSABLE_CONTENT,
    ):
        client_status = status.HTTP_400_BAD_REQUEST
    else:
        client_status = status.HTTP_502_BAD_GATEWAY

    body: dict[str, object] = {
        'code': 'UPSTREAM_HTTP_ERROR',
        'message': message,
        'upstream_status': upstream_status,
        'upstream_body': text,
    }
    if isinstance(parsed, (dict, list)):
        body['upstream_json'] = sanitize_for_json(parsed)
    if bank_message:
        body['upstream_message'] = bank_message

    return client_status, body


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'code': 'VALIDATION_ERROR',
            'message': 'Erro de validação',
            'errors': sanitize_for_json(exc.errors()),
        },
    )


async def custom_exception_handler(
    request: Request,
    exc: Union[DomainException, MultipleException, InfrastructureException, Exception],
) -> JSONResponse:
    if isinstance(exc, httpx.HTTPStatusError):
        client_status, content = _upstream_http_error_response_content(exc.response)
        return JSONResponse(
            status_code=client_status,
            content=sanitize_for_json(content),
        )
    if isinstance(exc, MultipleException):
        status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
        errors = []
        for error in exc.args:
            error_message = get_from_sequence(error.args, 0, '')
            error_field = get_from_sequence(error.args, 1)
            error_code = getattr(error, 'code', 'HTTP_ERROR')
            errors.append({
                'field': error_field,
                'code': error_code,
                'message': error_message,
            })
        return JSONResponse(status_code=status_code, content=errors)
    status_code = getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
    code = getattr(exc, 'code', 'HTTP_ERROR')
    return JSONResponse(
        status_code=status_code,
        content={
            'code': code,
            'message': str(exc),
        },
    )
