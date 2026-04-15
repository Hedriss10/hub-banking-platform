# Hub Banking Platform

Plataforma de automação financeira: API **REST** em **FastAPI** (Python 3.13), persistência em **PostgreSQL**, migrações com **Alembic**, empacotamento com **Poetry** e **Docker**.

## Stack

| Camada | Tecnologia |
|--------|------------|
| API | FastAPI · Uvicorn · OpenAPI (`/docs` em modo debug) |
| Dados | PostgreSQL 15 · SQLAlchemy 2 async · asyncpg |
| Migrações | Alembic (`migrations/`) |
| Segurança | JWT · Argon2 (hash de senhas) |
| Ambiente | Poetry · Docker Compose |

## Pré-requisitos

- **Python** ≥ 3.13  
- **Poetry**  
- **Docker** e **Docker Compose** (para subir Postgres + API via Compose)

## Configuração rápida

1. Copie as variáveis de ambiente e preencha os valores necessários:

   ```bash
   cp env.example.env .env
   ```

2. Instale dependências:

   ```bash
   poetry install
   ```

3. Ajuste `SQLALCHEMY_DATABASE_URI` e demais chaves no `.env` (veja `env.example.env`).

## Executar localmente (sem Docker só da API)

Com Postgres acessível conforme o `.env`:

```bash
make run
```

Ou diretamente (usa `API_PORT` do `.env`):

```bash
poetry run uvicorn src.main:app --reload --workers 3 --port <PORTA>
```

## Docker Compose (Postgres + API)

Na raiz do repositório, com `.env` válido:

```bash
make build   # ou: make up
make logs    # acompanhar logs
make down    # parar e remover containers (volumes com -v)
```

O serviço da API usa o `Dockerfile` em `docker/Dockerfile` e a rede interna `hub-banking-platform-net`. O compose documenta que o **Nginx Daycoval** fica no **host** da VPS; confira `deploy/` e comentários em `docker/docker-compose.yml`.

## Comandos úteis (`Makefile`)

| Comando | Descrição |
|---------|-----------|
| `make run` | Sobe Uvicorn em desenvolvimento |
| `make build` / `make up` / `make down` | Compose conforme `docker/docker-compose.yml` |
| `make logs` | Logs em tempo real dos containers |
| `make formatter` | Formata com Black |
| `make lint` | Ruff + verificação Black |
| `make init-db` | `alembic upgrade head` |

## Estrutura do código

- `src/interface/` — rotas HTTP, controllers, schemas, middlewares  
- `src/domain/` — casos de uso, serviços, DTOs, contratos de repositório  
- `src/infrastructure/` — repositórios Postgres, modelos ORM, JWT, integrações (`external_apis/`)  
- `src/core/` — configurações, logging, exceções transversais  

Prefixo da API: `/api` (versão **v2** em `src/interface/api/v2/`).

## Arquitetura (visão geral)

O diagrama abaixo resume clientes, containers, camadas internas e o **gateway Daycoval (sandbox)**. O exemplo de **Nginx** em `deploy/nginx-daycoval-sandbox.conf` faz *proxy* **HTTPS** para `apigwsandbox.daycoval.com.br` (testes de integração no host); o acesso à **API Hub** no Compose é tipicamente direto na porta configurada (`API_PORT`), não passando por esse Nginx.

```mermaid
%%{init: {'theme': 'neutral', 'flowchart': {'htmlLabels': false}}}%%
flowchart TB
  classDef app fill:#d6e8fa,stroke:#2166ac,stroke-width:2px;
  classDef data fill:#fff4cc,stroke:#b08a00,stroke-width:2px;
  classDef external fill:#fde8e8,stroke:#c62828,stroke-width:2px,stroke-dasharray: 4 3;
  classDef infra fill:#eceff1,stroke:#607d8b,stroke-width:2px;

  subgraph C["Clientes"]
    Web["Cliente HTTP · REST"]:::app
  end

  subgraph R["Edge no host (opcional)"]
    Nginx["Nginx :8080 · proxy Daycoval"]:::infra
  end

  subgraph P["Docker Compose"]
    API["API FastAPI 3.13 · Uvicorn :8000"]:::app
    DB[("PostgreSQL 15 · dados")]:::data
    MIG["Alembic · schema"]:::infra
    API -->|async SQL · asyncpg| DB
    MIG -->|migrações| DB
  end

  subgraph L["Camadas do código"]
    IF["Interface · rotas e HTTP"]:::app
    DOM["Domínio · casos de uso"]:::app
    INF["Infra · repos e integrações"]:::infra
    CORE["Core · config e logs"]:::infra
    IF --> DOM --> INF
    DOM --> CORE
  end

  subgraph E["Externo · sandbox"]
    GW["apigwsandbox.daycoval.com.br"]:::external
  end

  Web -->|REST JSON v2| API
  Nginx -->|TLS upstream| GW
  API -.->|estrutura| IF
  INF -->|integrações HTTPS| GW
```

## Licença e autoria

Ver `pyproject.toml` para metadados do projeto.
