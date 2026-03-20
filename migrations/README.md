# Migrações Alembic

- Configuração: `alembic.ini` (raiz) e `env.py` (sobe a app Flask, carrega modelos e usa a **engine com o Postgres ligado**).
- **Modo offline** (`--sql`, etc.) não é suportado: o Postgres tem de estar acessível via `SQLALCHEMY_DATABASE_URI`.
- `load_all_models()` importa `src.models.*` para o Alembic ver tabelas novas no autogenerate.

Na raiz do repositório:

```bash
alembic upgrade head
alembic revision --autogenerate -m "sua mensagem"
```

Ou `make migrate` e `make revision m="sua mensagem"`.

Carregue o `.env` (ou exporte `SQLALCHEMY_DATABASE_URI`) antes de correr os comandos.
