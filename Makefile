#!/usr/bin/make

include .env

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally."
	@echo "    run"
	@echo "        Run development local application."
	@echo "    build"
	@echo "        Run docker compose and force build containers."
	@echo "    up"
	@echo "        Run docker compose and force up containers."
	@echo "    down"
	@echo "        Stop development docker compose and remove containers."
	@echo "    logs"
	@echo "        Exibe os logs dos containers em tempo real."
	@echo "    deploy"
	@echo "        Build and push production image to Docker Hub."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with ruff, and check if black formatter should be applied."
	@echo "    lint-watch"
	@echo "        Lint code with ruff in watch mode."
	@echo "    lint-fix"
	@echo "        Lint code with ruff and try to fix."
	@echo "    reset-db"
	@echo "        Apaga schema, tabelas, dados e histórico do Alembic no Postgres local."
	@echo "    reset-db-volume"
	@echo "        Remove o volume Docker do Postgres e recria o banco do zero."
	@echo "    migrate-autogen"
	@echo "        Gera nova migração Alembic a partir dos models (use MSG=\"texto\")."
	@echo "    init-db"
	@echo "        Aplica migrações Alembic e cria usuário dev padrão."
	@echo "    seed"
	@echo "        Cria usuário de desenvolvimento (usuario.dev@hotmail.com)."

# Docker Compose - usa arquivos da pasta docker/ e .env para variáveis
COMPOSE := docker compose -f docker/docker-compose.yml --project-directory . --env-file .env
LOCAL_SQLALCHEMY_DATABASE_URI := postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)
LOCAL_REDIS_URL := redis://$(POSTGRES_HOST):$(REDIS_PORT)/0
MSG ?= migration

DEPLOY_IMAGE := docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t hedris10/hub-banking-platform:latest \
  --push .

run:
	poetry run uvicorn src.main:app --reload --workers 3 --port $(API_PORT)

build:
	$(COMPOSE) up -d --build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

deploy:
	$(DEPLOY_IMAGE)

formatter:
	poetry run black src

lint:
	poetry run ruff check --fix src && poetry run black --check src

mypy:
	poetry run mypy .

lint-watch:
	poetry run ruff src --watch

lint-fix:
	poetry run ruff src --fix

init-db:
	SQLALCHEMY_DATABASE_URI=$(LOCAL_SQLALCHEMY_DATABASE_URI) poetry run alembic upgrade head
	$(MAKE) seed

seed:
	SQLALCHEMY_DATABASE_URI=$(LOCAL_SQLALCHEMY_DATABASE_URI) \
	poetry run python -c "from src.infrastructure.seed.init_system import main; main()"

migrate-autogen:
	SQLALCHEMY_DATABASE_URI=$(LOCAL_SQLALCHEMY_DATABASE_URI) poetry run alembic revision --autogenerate -m "$(MSG)"

reset-db:
	@./entrypoints/reset-db.sh

reset-db-volume:
	$(COMPOSE) down -v
	$(COMPOSE) up -d hub-banking-platform
	@echo "✅ Volume do PostgreSQL removido. Aguarde o healthcheck e rode: make init-db"

alembic-init:
	poetry run alembic init migrations
