# Arquitetura — Sentinela AI

## Visão Geral

```
Sua aplicação
    │
    │  @observe()  ←──── decorator do SDK
    │
    ▼
SDK Python  ──── POST /traces ────►  Servidor FastAPI
                                          │
                                    Salva no PostgreSQL
                                          │
                                    Celery .delay()
                                          │
                                          ▼
                                     Fila Redis
                                          │
                                    Worker Celery
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         Avaliadores  Guardrails  Benchmark
                              │
                        Salva ResultadoAvaliacao
                              │
                              ▼
                        PostgreSQL
                              │
                              ▼
                   Dashboard Streamlit  ←── GET /traces, /analytics, /drift
```

## Componentes

### SDK (`sdk/`)
Biblioteca Python instalada na aplicação do usuário. Responsável por capturar traces e enviá-los ao servidor de forma assíncrona e não-bloqueante.

### Servidor (`servidor/`)
API FastAPI que recebe traces, persiste no banco e delega avaliações ao Celery. Expõe endpoints REST para o dashboard e integrações externas.

### Workers (`servidor/app/workers/`)
Processos Celery que rodam em paralelo ao servidor. Executam tarefas pesadas em background:
- `worker_avaliacao` — roda os avaliadores LLM-as-Judge
- `worker_analytics` — agrega métricas horárias
- `worker_alerta` — verifica regras de alerta a cada 5min
- `worker_benchmark` — roda benchmarks em datasets

### Dashboard (`dashboard/`)
Interface Streamlit que consome a API REST do servidor. Sem acesso direto ao banco.

## Decisões de Design

### Por que BackgroundTasks → Celery?
`BackgroundTasks` do FastAPI roda na mesma thread do servidor — se o worker travar, trava o servidor. Celery isola completamente o processamento.

### Por que o SDK não depende do servidor?
Falhas no servidor Sentinela nunca afetam a aplicação monitorada. O SDK captura erros silenciosamente e continua.

### Por que os schemas Pydantic são duplicados?
SDK e servidor têm schemas separados para evitar acoplamento de pacote. Cada um pode evoluir independentemente.
