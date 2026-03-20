# Docker

## Poetry na imagem

O build usa `pyproject.toml` + `poetry.lock` para instalar as mesmas versões que no ambiente local.

## Variáveis de ambiente (uma só `.env`)

Usa **apenas** o ficheiro `.env` na **raiz do repositório** (junto a `manage.py`). O `Makefile` invoca o Compose com `--project-directory` apontando para essa raiz, para o Docker carregar esse `.env` na interpolação `${VAR:-padrao}` do `docker-compose.yml`.

Copia o modelo:

```bash
cp .env.example .env
```

Para a API dentro do Compose falar com o Postgres, define na raiz (ou deixa o default do compose):

`SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://hub:hub@db:5432/hub_banking`

(o hostname `db` é o nome do serviço na rede Docker).

## Gunicorn

A configuração do servidor WSGI está em [`config/gunicorn.conf.py`](../config/gunicorn.conf.py), não na raiz do projeto.
