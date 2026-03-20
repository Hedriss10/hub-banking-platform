.PHONY: help install install-dev lint format test run docker-build docker-up docker-down docker-logs migrate revision clean

PYTHON ?= python3
PIP ?= pip
# Raiz do repo: Compose carrega `.env` daqui (uma única fonte; não uses docker/.env)
PROJECT_ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
COMPOSE := docker compose --project-directory "$(PROJECT_ROOT)" -f docker/docker-compose.yml

help:
	@echo "Alvos principais:"
	@echo "  make install       — dependências de produção (pip -r requirements.txt)"
	@echo "  make install-dev   — dev (ruff, pytest, etc. via pyproject / pip)"
	@echo "  make lint          — ruff check + format"
	@echo "  make test          — pytest com cobertura"
	@echo "  make run           — Flask em manage.py (porta 5001, debug)"
	@echo "  make docker-build  — imagem da API"
	@echo "  make docker-up     — Compose (usa .env na raiz do repo)"
	@echo "  make docker-down   — para e remove containers (mantém volume)"
	@echo "  make migrate       — alembic upgrade head (requer .env / URI)"
	@echo "  make revision m=\"msg\" — nova revisão Alembic (autogenerate)"

install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install "pytest>=8.3.5" "pytest-cov>=6.1" "ruff>=0.11" "pytest-dotenv>=0.5" "bandit>=1.8"

lint:
	ruff check src tests config --fix && ruff format src tests config

format:
	ruff format src tests config

test:
	pytest tests -v --cov=src --cov-report=term-missing

run:
	cd $(PROJECT_ROOT) && $(PYTHON) manage.py

docker-build:
	$(COMPOSE) build api

docker-up:
	$(COMPOSE) up -d

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f api

migrate:
	cd $(PROJECT_ROOT) && alembic upgrade head

m ?= describe-your-change
revision:
	cd $(PROJECT_ROOT) && alembic revision --autogenerate -m "$(m)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
