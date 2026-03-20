#!/bin/bash
set -e

echo "🔄 Executando migrações do banco de dados..."
alembic upgrade head
