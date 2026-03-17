#!/bin/bash
set -e

echo "📦 Inicializando aplicação..."

./entrypoints/init-db.sh

echo "🚀 Subindo aplicação..."
exec "$@"
