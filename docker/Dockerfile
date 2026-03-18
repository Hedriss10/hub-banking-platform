FROM python:3.13-slim

WORKDIR /src

ENV PYTHONPATH=/src

# Dependências do Postgres + compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libpq-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --upgrade pip && pip install poetry

# Copiar manifesto antes do código
COPY pyproject.toml poetry.lock ./

# IMPORTANTE: desabilitar venv do poetry
RUN poetry config virtualenvs.create false

# Instalar libs (apenas deps principais - dev não necessário no container)
RUN poetry install --no-root --no-interaction --no-ansi

# Agora copiar código
COPY src /src/src
COPY alembic.ini .
COPY migrations /src/migrations
COPY entrypoints /src/entrypoints

# Rodar migrações no container
RUN chmod +x /src/entrypoints/*.sh

ENTRYPOINT ["/src/entrypoints/init-app.sh"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
