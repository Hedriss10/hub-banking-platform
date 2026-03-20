# Build a partir da raiz: docker build -f docker/Dockerfile .
#
# Usa Poetry para instalar dependências a partir de pyproject.toml + poetry.lock
# (mesma fonte de verdade que no teu ambiente local).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && pip install --no-cache-dir "poetry>=2.0,<3" \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Só manifestos primeiro (melhor cache de camadas quando mudas código)
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root --no-ansi \
    && rm -rf "${POETRY_CACHE_DIR}"

COPY . .
RUN poetry install --without dev --no-ansi \
    && rm -rf "${POETRY_CACHE_DIR}"

EXPOSE 8001

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "manage:app"]
