#!/bin/bash
set -e

echo "=== Deploy Sentinela AI ==="

# Verifica se .env.prod existe
if [ ! -f .env.prod ]; then
  echo "ERRO: .env.prod não encontrado. Copie .env.prod.example e preencha as variáveis."
  exit 1
fi

# Carrega variáveis do .env.prod para o script (necessário para POSTGRES_PASSWORD no compose)
set -a
source .env.prod
set +a

echo ">> Atualizando código..."
git pull origin main

echo ">> Buildando imagens..."
docker compose -f docker-compose.prod.yml build --no-cache

echo ">> Aplicando migrations..."
docker compose -f docker-compose.prod.yml run --rm servidor alembic upgrade head

echo ">> Subindo serviços..."
docker compose -f docker-compose.prod.yml up -d

echo ">> Status dos containers:"
docker compose -f docker-compose.prod.yml ps

echo "=== Deploy concluído ==="
echo "Dashboard: https://sentinela.klauberfischer.online"
echo "API docs:  https://api.sentinela.klauberfischer.online/docs"
