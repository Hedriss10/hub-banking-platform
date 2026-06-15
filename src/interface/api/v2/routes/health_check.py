import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.core.config.settings import get_settings
from src.infrastructure.database.session import get_engine
from src.infrastructure.redis.client import get_redis_client
from src.interface.api.v2.schemas.health_check import (
    ComponentHealthSchema,
    HealthCheckResponseSchema,
    HealthChecksSchema,
    HealthStatus,
)

tags_metadata = {
    'name': 'Health Check',
    'description': 'Verificação de saúde da aplicação e dependências.',
}

router = APIRouter(
    prefix='/health',
    tags=[tags_metadata['name']],
)

_CHECK_TIMEOUT_SECONDS = 5


async def _check_application() -> ComponentHealthSchema:
    return ComponentHealthSchema(status='healthy')


async def _check_database() -> ComponentHealthSchema:
    try:
        async with asyncio.timeout(_CHECK_TIMEOUT_SECONDS):
            engine = get_engine()
            async with engine.connect() as connection:
                await connection.execute(text('SELECT 1'))
        return ComponentHealthSchema(status='healthy')
    except Exception as error:
        return ComponentHealthSchema(status='unhealthy', detail=str(error))


async def _check_redis() -> ComponentHealthSchema:
    settings = get_settings()
    if not settings.REDIS_URL:
        return ComponentHealthSchema(
            status='unhealthy',
            detail='REDIS_URL não configurado',
        )

    try:
        async with asyncio.timeout(_CHECK_TIMEOUT_SECONDS):
            redis_client = await get_redis_client()
            if not await redis_client.ping():
                return ComponentHealthSchema(
                    status='unhealthy',
                    detail='Redis não respondeu ao PING',
                )
        return ComponentHealthSchema(status='healthy')
    except Exception as error:
        return ComponentHealthSchema(status='unhealthy', detail=str(error))


def _overall_status(*checks: ComponentHealthSchema) -> HealthStatus:
    if all(check.status == 'healthy' for check in checks):
        return 'healthy'
    return 'unhealthy'


@router.get(
    '',
    response_model=HealthCheckResponseSchema,
    summary='Health check',
    description=(
        'Verifica a disponibilidade da aplicação, conexão com PostgreSQL e Redis.'
    ),
    responses={
        status.HTTP_200_OK: {'description': 'Todos os serviços estão saudáveis'},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            'description': 'Um ou mais serviços estão indisponíveis',
        },
    },
)
async def health_check() -> JSONResponse:
    settings = get_settings()

    application = await _check_application()
    database = await _check_database()
    redis = await _check_redis()

    checks = HealthChecksSchema(
        application=application,
        database=database,
        redis=redis,
    )
    overall = _overall_status(application, database, redis)
    payload = HealthCheckResponseSchema(
        status=overall,
        app_name=settings.APP_NAME,
        version=settings.API_VERSION,
        checks=checks,
    )

    status_code = (
        status.HTTP_200_OK
        if overall == 'healthy'
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )
