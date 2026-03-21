# 📊 STATUS — Sentinela AI

> Arquivo de controle de features, progresso e decisões técnicas.
> Atualizar sempre que uma feature for iniciada, concluída ou alterada.

---

## Estado Geral

| Item | Status |
|------|--------|
| Escopo definido | ✅ Concluído |
| README | ✅ Concluído |
| Estrutura de pastas | ✅ Concluído |
| Infraestrutura Docker | ✅ Concluído |
| SDK Python | ✅ Concluído |
| Backend (FastAPI) | ✅ Concluído |
| Workers Celery | ✅ Concluído |
| 7 Avaliadores | ✅ Concluído |
| API Analytics | ✅ Concluído |
| Dashboard (3 páginas) | ✅ Concluído |
| Documentação | ⏳ Pendente |

---

## Fase 1 — Core (Base do sistema)

> Objetivo: sistema funcionando de ponta a ponta, sem features avançadas.

### SDK Python (`sdk/`)

| Feature | Status | Notas |
|---------|--------|-------|
| Decorator `@observe()` | ✅ Concluído | Captura input, output, latência — sync e async |
| Cliente HTTP async | ✅ Concluído | Fire-and-forget, falhas não propagam |
| Pydantic models (Trace, Span) | ✅ Concluído | `sdk/sentinela/modelos.py` |
| Callback handler LangChain | ✅ Concluído | `sdk/sentinela/integracoes/langchain.py` |
| Publicação no PyPI | ⏳ Pendente | `pip install sentinela-ai` |

### Backend (`servidor/`)

| Feature | Status | Notas |
|---------|--------|-------|
| Setup FastAPI + estrutura de pastas | ✅ Concluído | |
| Configuração com Pydantic Settings | ✅ Concluído | `app/configuracao.py` |
| Conexão PostgreSQL (SQLAlchemy async) | ✅ Concluído | `app/bd/sessao.py` |
| Migrations com Alembic | ✅ Concluído | `app/bd/migracoes/env.py` |
| `POST /traces` — ingestão de traces | ✅ Concluído | `app/api/ingestao.py` |
| `GET /traces` — listagem com filtros | ✅ Concluído | `app/api/traces.py` + `GET /traces/{id}` |
| ORM models: Trace, ResultadoAvaliacao | ✅ Concluído | `app/modelos/trace.py` |
| Docker + docker-compose | ✅ Concluído | API + PostgreSQL + Redis + Dashboard |

### Avaliadores básicos

| Avaliador | Status | Notas |
|-----------|--------|-------|
| Classe base `AvaliadorBase` | ✅ Concluído | `app/avaliadores/base.py` |
| `Faithfulness` (LLM-as-Judge) | ✅ Concluído | `app/avaliadores/faithfulness.py` |
| `Relevância` (LLM-as-Judge) | ✅ Concluído | `app/avaliadores/relevancia.py` |

### Dashboard básico (`dashboard/`)

| Feature | Status | Notas |
|---------|--------|-------|
| Setup Streamlit | ✅ Concluído | `dashboard/app.py` |
| Página: Visão Geral (KPIs) | ✅ Concluído | `dashboard/paginas/visao_geral.py` |
| Página: Traces (lista + filtros) | ✅ Concluído | `dashboard/paginas/traces.py` |
| Componente: Visualizador de trace | ✅ Concluído | Drill-down inline com scores e raciocínio |

---

## Fase 2 — Motor de Avaliação

> Objetivo: evals rodando em background, mais avaliadores, dashboard com trends.

### Workers Celery

| Feature | Status | Notas |
|---------|--------|-------|
| Setup Celery + Redis | ✅ Concluído | `app/workers/celery_app.py` |
| Worker de avaliação (background) | ✅ Concluído | `app/workers/worker_avaliacao.py` — retry automático |
| Worker de analytics (hourly) | ✅ Concluído | `app/workers/worker_analytics.py` + Celery Beat |

### Avaliadores adicionais

| Avaliador | Status | Notas |
|-----------|--------|-------|
| `Toxicidade` (LLM-as-Judge) | ✅ Concluído | `app/avaliadores/toxicidade.py` |
| `Coerência` (LLM-as-Judge) | ✅ Concluído | `app/avaliadores/coerencia.py` |
| `Detecção de PII` (Regex) | ✅ Concluído | `app/avaliadores/deteccao_pii.py` — CPF, CNPJ, e-mail, tel, cartão |
| `Eficiência de Custo` (Métrica) | ✅ Concluído | `app/avaliadores/eficiencia_custo.py` — tabela de preços por modelo |
| `Customizado` (prompt definido pelo usuário) | ✅ Concluído | `app/avaliadores/customizado.py` |

### ORM e API

| Feature | Status | Notas |
|---------|--------|-------|
| ORM: ResultadoAvaliacao | ✅ Concluído | Fase 1 |
| `GET /avaliacoes` — resultados por trace | ✅ Concluído | Embutido no `GET /traces/{id}` |
| `GET /analytics/scores` — trends e scores | ✅ Concluído | `app/api/analytics.py` |
| `GET /analytics/volume` — volume por dia | ✅ Concluído | |
| `GET /analytics/projetos` — resumo por projeto | ✅ Concluído | |

### Dashboard

| Feature | Status | Notas |
|---------|--------|-------|
| Página: Avaliações com trends | ✅ Concluído | `dashboard/paginas/avaliacoes.py` |
| Componente: Score card com tendência | ✅ Concluído | Métricas com delta de aprovação |
| Componente: Heatmap avaliador × dia | ✅ Concluído | Visualização rápida de degradação |
| Componente: Gráficos reutilizáveis | ✅ Concluído | `dashboard/componentes/graficos.py` |

---

## Fase 3 — Inteligência

> Objetivo: guardrails, drift detection, alertas, datasets e regression testing.

### Guardrails

| Feature | Status | Notas |
|---------|--------|-------|
| Modo síncrono (bloqueia resposta) | ⏳ Pendente | `@observe(guardrails=["sem_pii"])` |
| Modo assíncrono (só loga) | ⏳ Pendente | `@observe(guardrails_modo="async")` |
| Guardrail: sem PII | ⏳ Pendente | |
| Guardrail: sem toxicidade | ⏳ Pendente | |
| Guardrail: on-topic | ⏳ Pendente | |

### Drift Detection

| Feature | Status | Notas |
|---------|--------|-------|
| Comparação de janelas de tempo | ⏳ Pendente | Semana atual vs. semana anterior |
| Identificação de possíveis causas | ⏳ Pendente | |
| API: `GET /drift` | ⏳ Pendente | |

### Datasets e Regression Testing

| Feature | Status | Notas |
|---------|--------|-------|
| ORM: Dataset, ItemDataset | ⏳ Pendente | |
| `CRUD /datasets` | ⏳ Pendente | |
| Criar dataset a partir de traces reais | ⏳ Pendente | Filtra por score alto |
| Rodar benchmark em dataset | ⏳ Pendente | `sentinela.run_benchmark(...)` |
| Dataset: vertice_ai_golden.json | ⏳ Pendente | 50 perguntas + respostas esperadas |
| Dataset: postador_golden.json | ⏳ Pendente | 30 prompts + outputs esperados |

### Alertas

| Feature | Status | Notas |
|---------|--------|-------|
| ORM: Alerta, RegraAlerta | ⏳ Pendente | |
| Worker de checagem de alertas | ⏳ Pendente | |
| Webhook Slack | ⏳ Pendente | |
| Webhook Discord | ⏳ Pendente | |
| `CRUD /alertas` — regras de alerta | ⏳ Pendente | |
| Dashboard: Página de Alertas | ⏳ Pendente | |

---

## Fase 4 — Polimento

> Objetivo: projeto pronto para portfólio e demo pública.

### Dashboard

| Feature | Status | Notas |
|---------|--------|-------|
| Página: Comparações A/B | ⏳ Pendente | Prompt v1 vs v2, Modelo A vs B |
| Página: Datasets | ⏳ Pendente | Gerenciar datasets de regressão |

### Exemplos e Integrações

| Feature | Status | Notas |
|---------|--------|-------|
| Exemplo: Vértice AI (antes/depois) | ⏳ Pendente | |
| Exemplo: Postador (antes/depois) | ⏳ Pendente | |
| Exemplo: LangChain genérico | ⏳ Pendente | |

### DevX e Demo

| Feature | Status | Notas |
|---------|--------|-------|
| Script de seed de dados fake | ⏳ Pendente | Demo funcional sem dados reais |
| Script de benchmark | ⏳ Pendente | |
| Makefile (`make dev`, `make test`, `make seed`) | ⏳ Pendente | |
| GIF/vídeo demo no README | ⏳ Pendente | |
| `.env.example` | ⏳ Pendente | |

### Documentação

| Feature | Status | Notas |
|---------|--------|-------|
| `docs/arquitetura.md` | ⏳ Pendente | |
| `docs/referencia_sdk.md` | ⏳ Pendente | |
| `docs/avaliadores.md` | ⏳ Pendente | |
| `docs/avaliadores_customizados.md` | ⏳ Pendente | |
| `docs/deploy.md` | ⏳ Pendente | |

---

## Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| ✅ | Concluído |
| 🚧 | Em progresso |
| ⏳ | Pendente |
| ❌ | Bloqueado / Cancelado |
| 🔄 | Revisão necessária |

---

## Decisões Técnicas

> Registro de decisões de arquitetura para não perder contexto.

| Data | Decisão | Motivo |
|------|---------|--------|
| 2026-03-21 | Pastas e código em PT-BR | Padronização do projeto |
| 2026-03-21 | FastAPI + PostgreSQL + Celery + Redis | Stack robusta, padrão de mercado |
| 2026-03-21 | LLM-as-Judge para evaluators | Melhor custo-benefício vs. modelos especializados |
| 2026-03-21 | Streamlit para dashboard | Velocidade de desenvolvimento, visual sem frontend separado |
| 2026-03-21 | SDK via decorator `@observe()` | DX mínima: 3 linhas para instrumentar qualquer app |
| 2026-03-21 | Esquemas Pydantic no servidor separados do SDK | SDK e servidor independentes — sem acoplamento direto |
| 2026-03-21 | Avaliação em BackgroundTasks do FastAPI (Fase 1) | Simples, sem Celery. Migra para workers na Fase 2 |
| 2026-03-21 | auto-create de tabelas no startup (dev only) | Em produção usar Alembic via `make migracao` |

---

## Backlog / Ideias Futuras

> Features interessantes mas fora do escopo atual.

- [ ] Suporte a traces distribuídos (multi-serviço, OpenTelemetry)
- [ ] Integração nativa com LlamaIndex
- [ ] Comparação entre provedores (OpenAI vs Anthropic vs Gemini)
- [ ] Exportação de relatórios em PDF
- [ ] API pública com plano gratuito (SaaS)
- [ ] Autenticação multi-tenant (múltiplos projetos por conta)
- [ ] Métricas de A/B testing estatisticamente significativas
- [ ] Integração com CI/CD (GitHub Actions para benchmark automático)
