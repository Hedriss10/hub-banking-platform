from typing import Union

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
    Garante que não existam bytes na resposta JSON.

    O FastAPI tenta serializar bytes como utf-8 por padrão, o que pode quebrar
    quando o payload é binário (ex.: PNG).
    """
    if isinstance(obj, bytes):
        return f'<bytes:{len(obj)}>'
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    return obj


# Compat: testes/uso antigo
_sanitize_for_json = sanitize_for_json


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
