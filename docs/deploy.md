# Guia de Deploy

## Desenvolvimento (local)

```bash
# Clona e sobe tudo
git clone https://github.com/seu-usuario/sentinela-ai
cd sentinela-ai

cp .env.example .env
# edite .env com sua OPENAI_API_KEY

make dev
# API:       http://localhost:8000
# Dashboard: http://localhost:8501
# Docs:      http://localhost:8000/docs

# Popula com dados de demo
make seed
```

## Variáveis de Ambiente Obrigatórias

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL do PostgreSQL com driver asyncpg |
| `REDIS_URL` | URL do Redis |
| `OPENAI_API_KEY` | Chave da OpenAI para os avaliadores LLM-as-Judge |

## Variáveis Opcionais

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MODELO_AVALIACAO` | `gpt-4o-mini` | Modelo usado pelos avaliadores |
| `AMBIENTE` | `desenvolvimento` | Use `producao` para desativar logs verbose |
| `API_SECRET_KEY` | — | Chave para autenticação (a implementar) |

## Produção com Docker

```bash
# Build das imagens
docker-compose -f docker-compose.yml build

# Sobe em modo produção
AMBIENTE=producao docker-compose up -d

# Roda migrations
make migracao
```

## Escalonamento dos Workers

Para aumentar o throughput de avaliações:

```bash
# Sobe mais workers Celery
docker-compose up -d --scale worker=3
```

Cada worker processa tarefas de avaliação em paralelo.

## Monitoramento dos Workers

```bash
# Inspeciona filas e workers
make logs

# Shell no banco para queries diretas
make shell-bd
```

## Considerações de Segurança

- Troque `API_SECRET_KEY` por um valor forte em produção
- Use PostgreSQL com SSL em produção (`sslmode=require` na URL)
- Restrinja o CORS em `main.py` para os domínios autorizados
- Não exponha o Redis publicamente — use rede interna Docker
