from typing import Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware

from src.core.config.settings import get_settings
from src.core.exceptions.custom import (
    DomainException,
    InfrastructureException,
    MultipleException,
)
from src.infrastructure.database import load_all_models
from src.interface.api import app_router
from src.interface.api.v2 import v2_tags_metadata
from src.interface.api.v2.middlewares.exceptions import (
    custom_exception_handler,
    request_validation_exception_handler,
)

settings = get_settings()

title = f'{settings.APP_NAME} API v{settings.API_VERSION}'

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_tags=v2_tags_metadata,
)


# hellow word
@app.get(
    '/',
    tags=['Health Check'],
    summary='Redireciona para a documentação',
    description='Redireciona para a documentação',
)
async def root() -> dict[str, str]:
    return {'message': 'API Hub Banking Platform Acesse a Documentação em /docs'}


_cors_origins = [
    str(o).strip() for o in settings.BACKEND_CORS_ORIGINS if str(o).strip()
]
_user_regex = (settings.BACKEND_CORS_ORIGIN_REGEX or '').strip() or None
_allow_origin_regex: Optional[str] = _user_regex
_allow_credentials = True
if not _cors_origins and _allow_origin_regex is None:
    if settings.DEBUG:
        _allow_origin_regex = r'https?://(localhost|127\.0\.0\.1)(:\d+)?$'
    else:
        _allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_origin_regex=_allow_origin_regex,
    allow_methods=['*'],
    allow_headers=['*'],
)

load_all_models()

app.add_exception_handler(DomainException, custom_exception_handler)
app.add_exception_handler(InfrastructureException, custom_exception_handler)
app.add_exception_handler(MultipleException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, custom_exception_handler)

app.include_router(app_router)
