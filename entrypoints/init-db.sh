#!/bin/bash
set -e

echo "🔄 Executando migrações do banco de dados..."
cd /src && alembic upgrade head
