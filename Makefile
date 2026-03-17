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
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with ruff, and check if black formatter should be applied."
	@echo "    lint-watch"
	@echo "        Lint code with ruff in watch mode."
	@echo "    lint-fix"
	@echo "        Lint code with ruff and try to fix."

# Docker Compose - usa arquivos da pasta docker/
COMPOSE := docker compose -f docker/docker-compose.yml --project-directory .

run:
	poetry run uvicorn src.main:app --reload --workers 3 --port $(API_PORT)

build:
	$(COMPOSE) up -d --build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down -v

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
	poetry run alembic upgrade head

alembic-init:
	poetry run alembic init migrations
