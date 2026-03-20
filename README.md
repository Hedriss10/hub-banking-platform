# CRM — Backend Athenas

API Flask (Flask-RESTX) para correspondentes bancários: colaboradores, operações, finanças e integrações com bancos.

---

## Objetivo

- Gestão de colaboradores e operações.
- Integração com APIs de bancos (Facta, Master, Daycoval, Bradesco, etc.).
- LGPD e dados sensíveis tratados com cuidado no desenho dos fluxos.
- Automação de comissões e relatórios.

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| API | Flask, Flask-RESTX, Flask-JWT-Extended, Flask-CORS |
| Persistência | PostgreSQL, SQLAlchemy, Flask-SQLAlchemy |
| Servidor WSGI | Gunicorn |
| Migrações | Alembic |

---

## Arquitetura (MVC adaptado)

O projeto não usa pastas com os nomes clássicos “MVC”, mas o papel de cada camada é este:

| Papel MVC | Pasta / módulo | Responsabilidade |
|-----------|----------------|------------------|
| **View** (contrato HTTP) | `src/resource/` | Namespaces RESTX, parsing de query/body, delegação |
| **Controller** (fino) | Mesmos arquivos em `resource/` | Orquestrar request → core e devolver `Response` |
| **Model** | `src/models/` | Entidades ORM (`db.Model`) |
| **“Service” / regras** | `src/core/` | Consultas, regras de negócio, uso de `db.session` |
| **Infra** | `src/database/`, `src/settings/` | Conexão SQLAlchemy, configuração por ambiente |

Boas práticas para evoluir:

1. Manter `resource/` fino: validação + chamar uma classe em `core/`.
2. Evitar SQL e regras pesadas dentro de `resource/`.
3. Respostas padronizadas via `src/service/response.py`.

---

## Estrutura de diretórios

```text
.
├── manage.py              # App WSGI (Gunicorn: manage:app)
├── .env.example           # Modelo único (raiz); Compose e app leem daqui
├── config/
│   └── gunicorn.conf.py   # WSGI (produção / Docker)
├── requirements.txt
├── pyproject.toml
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── migrations/            # Alembic
└── src/
    ├── app.py             # create_app(), registro de namespaces
    ├── core/              # Regras e acesso a dados
    ├── db/
    ├── models/
    ├── resource/          # Endpoints (RESTX)
    ├── service/
    ├── settings/
    └── utils/
```

---

## Configuração

1. Copie variáveis de ambiente:

   ```bash
   cp .env.example .env
   ```

   Para **Docker Compose**, mantém o mesmo `.env` na raiz: o `make docker-up` usa `--project-directory` para o Compose interpolar variáveis a partir desse ficheiro. Com a API no Compose, usa host `db` na URI (exemplo no `.env.example`).

2. Ajuste `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY` e `JWT_SECRET_KEY`.

3. Instalação local:

   ```bash
   make install
   # ou: pip install -r requirements.txt
   ```

4. Migrações (com banco já criado e URI válida):

   ```bash
   make migrate
   ```

5. Nova revisão após alterar modelos:

   ```bash
   make revision m="descreva a mudança"
   ```

---

## Uso local

```bash
make run
# Servidor de desenvolvimento: http://0.0.0.0:5001
```

Produção (exemplo):

```bash
gunicorn -c config/gunicorn.conf.py "manage:app"
```

Documentação Swagger: prefixo da API vem de `APPLICATION_ROOT` em `src/settings/_base.py` (ex.: `/dev` em desenvolvimento) e `DOCS` / `DOCS_DEV` para o path do doc.

---

## Docker

A imagem é construída com **Poetry** (`pyproject.toml` + `poetry.lock`). Detalhes em [docker/README.md](docker/README.md). Configuração WSGI: `config/gunicorn.conf.py`.

Na raiz do repositório:

```bash
make docker-build
make docker-up
```

- **API**: porta `8001` (padrão em `config/gunicorn.conf.py`; `GUNICORN_BIND` / `API_PORT` no `.env` da raiz).
- **PostgreSQL**: porta `5432` por padrão; credenciais e portas vêm do `.env` na **raiz** (variáveis `POSTGRES_*`, etc., com fallback no YAML).

Logs da API:

```bash
make docker-logs
```

Parar:

```bash
make docker-down
```

---

## Makefile

| Alvo | Descrição |
|------|-----------|
| `make help` | Lista os comandos |
| `make install` | `pip install -r requirements.txt` |
| `make install-dev` | Dependências de desenvolvimento (pytest, ruff, …) |
| `make lint` | Ruff check + format |
| `make test` | Pytest com cobertura |
| `make run` | `python manage.py` |
| `make docker-build` / `docker-up` / `docker-down` | Compose em `docker/` |
| `make migrate` | `alembic upgrade head` |
| `make revision m="msg"` | `alembic revision --autogenerate` |

---

## Testes

```bash
make install-dev
make test
```

Testes de integração com schema completo devem usar **PostgreSQL** (os modelos usam esquema `public` e FKs que não espelham bem em SQLite). O teste inicial em `tests/test_smoke.py` só valida que a app sobe.

---

## Autor

**Hedris Pereira** — Backend Athenas.
