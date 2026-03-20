# Migrações Alembic

- Configuração: `alembic.ini` (raiz) e `env.py` (carrega `create_app()` e metadados do SQLAlchemy).
- A partir da raiz do repositório:

  ```bash
  alembic upgrade head
  alembic revision --autogenerate -m "sua mensagem"
  ```

- Ou use `make migrate` e `make revision m="sua mensagem"`.

Defina `SQLALCHEMY_DATABASE_URI` no ambiente antes de rodar os comandos.
