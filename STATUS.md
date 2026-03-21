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
| Dashboard (6 páginas) | ✅ Concluído |
| Guardrails | ✅ Concluído |
| Drift Detection | ✅ Concluído |
| Dataset Management | ✅ Concluído |
| Alertas (Slack/Discord) | ✅ Concluído |
| Exemplos de integração | ✅ Concluído |
| Script de seed | ✅ Concluído |
| Documentação | ✅ Concluído |

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
| Modo assíncrono (avalia e loga, não bloqueia) | ✅ Concluído | `app/nucleo/guardrails.py` |
| Guardrail: sem PII | ✅ Concluído | Reutiliza `AvaliadorDeteccaoPII` |
| Guardrail: sem toxicidade | ✅ Concluído | Reutiliza `AvaliadorToxicidade` |
| Violações persistidas como `ResultadoAvaliacao` | ✅ Concluído | Prefixo `guardrail:` no avaliador |
| Ativado via metadata do trace | ✅ Concluído | `metadata={"guardrails": ["sem_pii"]}` |

### Drift Detection

| Feature | Status | Notas |
|---------|--------|-------|
| Comparação de janelas de tempo consecutivas | ✅ Concluído | `app/nucleo/detector_drift.py` |
| Threshold configurável (padrão: queda > 10%) | ✅ Concluído | `THRESHOLD_DRIFT = 0.10` |
| `GET /drift/{projeto}` | ✅ Concluído | `app/api/drift.py` — janela em horas |

### Datasets e Regression Testing

| Feature | Status | Notas |
|---------|--------|-------|
| ORM: Dataset, ItemDataset | ✅ Concluído | `app/modelos/dataset.py` |
| `CRUD /datasets` | ✅ Concluído | `app/api/datasets.py` |
| `POST /datasets/{id}/benchmark` | ✅ Concluído | Enfileira no Celery, retorna task_id |
| Worker de benchmark | ✅ Concluído | `app/workers/worker_benchmark.py` |
| Dataset: vertice_ai_golden.json | ⏳ Pendente | Fase 4 — seed de dados |
| Dataset: postador_golden.json | ⏳ Pendente | Fase 4 — seed de dados |

### Alertas

| Feature | Status | Notas |
|---------|--------|-------|
| ORM: Alerta, RegraAlerta | ✅ Concluído | `app/modelos/alerta.py` |
| Worker de checagem a cada 5 min (Celery Beat) | ✅ Concluído | `app/workers/worker_alerta.py` |
| Anti-spam: não repete alerta na mesma janela | ✅ Concluído | Checa histórico antes de disparar |
| Webhook Slack (com blocks formatados) | ✅ Concluído | `app/nucleo/notificador.py` |
| Webhook Discord (com embeds) | ✅ Concluído | |
| `CRUD /alertas/regras` | ✅ Concluído | `app/api/alertas.py` |
| `GET /alertas/historico` | ✅ Concluído | |
| Dashboard: Página de Alertas | ⏳ Pendente | Fase 4 |

---

## Fase 4 — Polimento

> Objetivo: projeto pronto para portfólio e demo pública.

### Dashboard

| Feature | Status | Notas |
|---------|--------|-------|
| Página: Comparações A/B | ✅ Concluído | `dashboard/paginas/comparacoes.py` |
| Página: Datasets | ✅ Concluído | `dashboard/paginas/datasets.py` |
| Página: Alertas | ✅ Concluído | `dashboard/paginas/alertas.py` — 3 abas |

### Exemplos e Integrações

| Feature | Status | Notas |
|---------|--------|-------|
| Exemplo: Vértice AI (antes/depois) | ✅ Concluído | `exemplos/vertice_ai/` |
| Exemplo: Postador (antes/depois) | ✅ Concluído | `exemplos/postador/` |
| Exemplo: LangChain genérico | ✅ Concluído | `exemplos/langchain_generico/` |

### DevX e Demo

| Feature | Status | Notas |
|---------|--------|-------|
| Script de seed de dados fake | ✅ Concluído | `scripts/popular_dados.py` — 7 dias de histórico |
| Makefile (`make dev`, `make seed`, `make teste`) | ✅ Concluído | |
| `.env.example` | ✅ Concluído | |
| GIF/vídeo demo no README | ⏳ Pendente | Gravar após subir o projeto |

### Documentação

| Feature | Status | Notas |
|---------|--------|-------|
| `docs/arquitetura.md` | ✅ Concluído | Diagrama de fluxo + decisões de design |
| `docs/referencia_sdk.md` | ✅ Concluído | API completa do SDK |
| `docs/avaliadores.md` | ✅ Concluído | Todos os 7 avaliadores documentados |
| `docs/avaliadores_customizados.md` | ✅ Concluído | 2 formas de criar avaliadores |
| `docs/deploy.md` | ✅ Concluído | Dev, produção e escalonamento |

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
