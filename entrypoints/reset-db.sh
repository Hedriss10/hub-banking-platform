#!/bin/bash
set -euo pipefail

CONTAINER_NAME="${POSTGRES_CONTAINER:-hub-banking-platform}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-hub-banking-platform}"
POSTGRES_SCHEMA="${POSTGRES_SCHEMA:-hub-banking-platform}"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
	echo "❌ Container PostgreSQL '$CONTAINER_NAME' não está rodando."
	echo "   Suba o banco com: make up"
	exit 1
fi

echo "🗑️  Apagando schema \"$POSTGRES_SCHEMA\" (tabelas, dados e Alembic)..."

docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<SQL
DROP SCHEMA IF EXISTS "$POSTGRES_SCHEMA" CASCADE;
CREATE SCHEMA "$POSTGRES_SCHEMA";
CREATE EXTENSION IF NOT EXISTS unaccent;
DROP TABLE IF EXISTS public.alembic_version;
SQL

echo "✅ Banco local resetado. Schema \"$POSTGRES_SCHEMA\" recriado vazio."
echo "   Gere uma nova migração: make migrate-autogen MSG=\"sua mensagem\""
echo "   Aplique no banco: make init-db"
