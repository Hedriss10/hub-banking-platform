"""Normalização da URI SQLAlchemy para o stack síncrono (psycopg2)."""


def ensure_sync_postgres_uri(uri: str | None) -> str | None:
    """
    URLs `postgresql+asyncpg://` exigem o pacote asyncpg; esta app usa psycopg2.
    """
    if not uri or '://' not in uri:
        return uri
    scheme, rest = uri.split('://', 1)
    if '+asyncpg' in scheme:
        scheme = scheme.replace('+asyncpg', '+psycopg2', 1)
        return f'{scheme}://{rest}'
    return uri
