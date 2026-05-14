from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from src.domain.dtos.safra import MargemBpoDto, MargemBpoOutputDto, SafraBatchSearchDto
from src.infrastructure.database.models.safra_batch_search import SafraBatchSearchModel
from src.infrastructure.database.session import get_session_factory
from src.infrastructure.redis.safra_batch_job_store import job_get, job_save
from src.infrastructure.repositories.safra_external import SafraExternalRepository

logger = logging.getLogger(__name__)


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    second = value.strip()
    if not second:
        return None
    if second.endswith('Z'):
        second = f'{second[:-1]}+00:00'
    try:
        dt = datetime.fromisoformat(second)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _margem_to_row_model(
    batch_job_id: UUID,
    row: SafraBatchSearchDto,
    out: MargemBpoOutputDto | None,
) -> SafraBatchSearchModel:
    data_admissao = _parse_iso_datetime(out.dataAdmissao) if out is not None else None
    return SafraBatchSearchModel(
        batch_job_id=batch_job_id,
        cpf=out.cpf if out is not None else row.cpf,
        margem=out.margem if out is not None else None,
        lotacao=out.lotacao if out is not None else None,
        autorizada=out.autorizada if out is not None else None,
        nome=out.nome if out is not None else None,
        secretaria=out.secretaria if out is not None else None,
        tipoServidor=out.tipoServidor if out is not None else None,
        cargo=out.cargo if out is not None else None,
        regimeJuridico=out.regimeJuridico if out is not None else None,
        dataAdmissao=data_admissao,
        uf=out.uf if out is not None else None,
        renda=out.renda if out is not None else None,
        phone_one=row.phone_one,
        phone_two=row.phone_two,
        phone_three=row.phone_three,
        phone_four=row.phone_four,
        phone_five=row.phone_five,
    )


async def run_safra_batch_job(job_id: UUID, rows_payload: list[dict[str, Any]]) -> None:
    """Processa cada linha do batch (consulta margem + persistência)."""
    try:
        rows = [SafraBatchSearchDto.model_validate(item) for item in rows_payload]
    except ValidationError as exc:
        logger.warning('batch safra job=%s payload inválido: %s', job_id, exc)
        await job_save(
            job_id,
            {
                'status': 'failed',
                'total_rows': len(rows_payload),
                'processed_rows': 0,
                'failed_rows': 0,
                'detail': 'Payload do job inválido',
            },
        )
        return

    repo = SafraExternalRepository()
    session_factory = get_session_factory()
    total = len(rows)

    existing = await job_get(job_id)
    if existing is None:
        existing = {}

    await job_save(
        job_id,
        {
            **existing,
            'status': 'processing',
            'total_rows': total,
            'processed_rows': 0,
            'failed_rows': 0,
            'detail': None,
        },
    )

    processed_ok = 0
    failed = 0

    try:
        async with session_factory() as session:
            for row in rows:
                dto = MargemBpoDto(
                    convenio=row.convenio,
                    cpf=row.cpf,
                    idProduto=row.idProduto,
                    matricula=row.matricula,
                )
                try:
                    out = await repo.get_margem_bpo(dto)
                except Exception as exc:
                    logger.warning(
                        'batch safra linha falhou job=%s cpf=%s: %s',
                        job_id,
                        row.cpf,
                        exc,
                    )
                    failed += 1
                    session.add(_margem_to_row_model(job_id, row, None))
                else:
                    processed_ok += 1
                    session.add(_margem_to_row_model(job_id, row, out))

                await session.flush()

                await job_save(
                    job_id,
                    {
                        'status': 'processing',
                        'total_rows': total,
                        'processed_rows': processed_ok + failed,
                        'failed_rows': failed,
                        'detail': None,
                    },
                )

            await session.commit()
    except Exception as exc:
        logger.exception('batch safra job=%s abortado', job_id)
        await job_save(
            job_id,
            {
                'status': 'failed',
                'total_rows': total,
                'processed_rows': processed_ok + failed,
                'failed_rows': failed,
                'detail': str(exc),
            },
        )
        return

    await job_save(
        job_id,
        {
            'status': 'completed',
            'total_rows': total,
            'processed_rows': processed_ok + failed,
            'failed_rows': failed,
            'detail': None,
        },
    )
