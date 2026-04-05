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
    docs_url='/docs' if settings.DEBUG else None,
    redoc_url='/redoc' if settings.DEBUG else None,
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


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
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
