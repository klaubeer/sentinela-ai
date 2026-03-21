# 🛡️ Sentinela AI

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/banco-PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/cache-Redis-DC382D?logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/LLM_Judge-OpenAI_GPT--4o--mini-412991?logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/containers-Docker-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/licença-MIT-green" alt="MIT"/>
</p>

<p align="center">
  <strong>Plataforma open-source de avaliação e observabilidade para LLMs em produção</strong>
</p>

<p align="center">
  <em>Você sabe quantas respostas do seu sistema de IA estão alucinando agora mesmo?<br/>
  O Sentinela sabe e te avisa antes que o usuário perceba.</em>
</p>

---

## O Problema

Equipes gastam semanas construindo RAG e agentes LLM, mas zero tempo monitorando se as respostas são boas. Quando descobrem que o modelo está alucinando ou gerando conteúdo tóxico, já perderam a confiança dos usuários — e às vezes causaram dano real.

**O Sentinela resolve isso.**

---

## O que é

O Sentinela AI é uma plataforma open-source de **avaliação e observabilidade** para aplicações baseadas em LLMs. Ele monitora, avalia e protege sistemas de IA em produção — capturando cada interação, rodando evaluations automáticos e alertando quando algo sai do esperado.

**Tagline:** *"Seu copiloto de qualidade para LLMs em produção"*

---

## Funcionalidades

- **Coleta automática de traces** — captura input, output, latência, tokens e custo de cada chamada LLM
- **Evaluation automático** — faithfulness, relevância, toxicidade, coerência e PII detection
- **Guardrails** — bloqueia ou loga respostas problemáticas antes de chegarem ao usuário
- **Drift detection** — detecta quando a qualidade das respostas cai ao longo do tempo
- **Regression testing** — testa datasets golden antes de mudar prompt ou modelo
- **Dashboard interativo** — visualiza tudo em tempo real com filtros, trends e comparações A/B
- **Alertas** — notifica via Slack ou Discord quando scores caem abaixo do threshold

---

## Quick Start

```bash
# 1. Sobe toda a infraestrutura
docker-compose up -d

# 2. Instala o SDK
pip install sentinela-ai
```

```python
# 3. Instrumenta em 3 linhas
from sentinela import Sentinela, observe

sentinela = Sentinela(api_key="sk-demo", base_url="http://localhost:8000")

@observe(name="meu-chatbot")
def meu_chatbot(pergunta: str) -> str:
    contexto = recuperar_documentos(pergunta)
    resposta = llm.invoke(pergunta, context=contexto)
    return resposta
```

Dashboard disponível em `http://localhost:8501`

---

## Integração com LangChain

```python
from sentinela.integracoes import SentinelaCallbackHandler

chain.invoke(input, config={"callbacks": [SentinelaCallbackHandler()]})
```

---

## Evaluators Disponíveis

| Evaluator | Tipo | O que mede |
|-----------|------|------------|
| **Faithfulness** | LLM-as-Judge | Resposta é fiel ao contexto RAG? |
| **Relevância** | LLM-as-Judge | Resposta realmente responde a pergunta? |
| **Toxicidade** | LLM-as-Judge | Linguagem inapropriada ou perigosa? |
| **Coerência** | LLM-as-Judge | Resposta é coerente e bem estruturada? |
| **Precisão de Contexto** | Heurística | Os documentos recuperados são relevantes? |
| **Latência** | Métrica | Tempo de resposta dentro do aceitável? |
| **Eficiência de Custo** | Métrica | Relação custo/qualidade satisfatória? |
| **Detecção de PII** | Regex + NER | Resposta vaza dados pessoais? |
| **Customizado** | Configurável | Qualquer critério definido via prompt |

---

## Tech Stack

| Camada | Tecnologia | Por quê |
|--------|-----------|---------|
| **API** | FastAPI | Async, rápida, tipada, padrão do mercado |
| **SDK** | Python (decorator) | Integração em 3 linhas |
| **Fila de Tarefas** | Celery + Redis | Evals rodam em background sem bloquear a app |
| **Banco de Dados** | PostgreSQL | Traces, scores, metadata e analytics |
| **Cache** | Redis | Rate limiting, cache de evals, pub/sub de alertas |
| **Motor de Evals** | Custom + RAGAS + DeepEval | Avaliação flexível e extensível |
| **Guardrails** | Custom | Bloqueio de PII, toxicidade e off-topic |
| **Dashboard** | Streamlit | Visual, interativo e rápido de construir |
| **Alertas** | Webhooks (Slack/Discord) | Notificação em tempo real |
| **Containerização** | Docker + docker-compose | Um comando para subir tudo |

---

## Estrutura do Projeto

```
sentinela-ai/
│
├── README.md
├── STATUS.md                        # Acompanhamento de features e progresso
├── docker-compose.yml               # Sobe tudo com um comando
├── Makefile                         # make dev, make test, make seed
├── .env.example
│
├── sdk/                             # 📦 SDK Python (o que as apps instalam)
│   ├── pyproject.toml
│   ├── sentinela/
│   │   ├── __init__.py              # from sentinela import observe, trace
│   │   ├── cliente.py               # Client HTTP async
│   │   ├── decoradores.py           # @observe() decorator
│   │   ├── middleware.py            # Middleware para LangChain/LlamaIndex
│   │   ├── integracoes/             # Integrações com frameworks
│   │   │   ├── langchain.py
│   │   │   └── llama_index.py
│   │   └── modelos.py               # Pydantic models (Trace, Span, Event)
│   └── testes/
│
├── servidor/                        # 🖥️ Backend da plataforma
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── configuracao.py          # Settings com Pydantic
│   │   │
│   │   ├── api/                     # Endpoints REST
│   │   │   ├── ingestao.py          # POST /traces — recebe traces do SDK
│   │   │   ├── traces.py            # GET /traces — lista e filtra traces
│   │   │   ├── avaliacoes.py        # GET /evals — resultados de avaliação
│   │   │   ├── datasets.py          # CRUD de datasets de teste
│   │   │   └── analytics.py         # Agregações, trends, comparações
│   │   │
│   │   ├── nucleo/                  # Lógica de negócio
│   │   │   ├── processador_trace.py # Processa e enriquece traces
│   │   │   ├── motor_avaliacao.py   # Orquestra evaluations
│   │   │   ├── guardrails.py        # Checagens de segurança
│   │   │   └── detector_drift.py    # Detecta degradação ao longo do tempo
│   │   │
│   │   ├── avaliadores/             # Avaliadores individuais
│   │   │   ├── base.py              # Classe base Avaliador
│   │   │   ├── faithfulness.py      # Resposta é fiel ao contexto?
│   │   │   ├── relevancia.py        # Resposta responde a pergunta?
│   │   │   ├── toxicidade.py        # Linguagem inapropriada?
│   │   │   ├── coerencia.py         # Resposta é coerente?
│   │   │   ├── eficiencia_custo.py  # Relação custo/qualidade
│   │   │   └── customizado.py       # Avaliador customizável por prompt
│   │   │
│   │   ├── modelos/                 # SQLAlchemy models (ORM)
│   │   │   ├── trace.py             # Trace, Span, Geracao
│   │   │   ├── resultado_avaliacao.py  # ResultadoAvaliacao, RodadaAvaliacao
│   │   │   ├── dataset.py           # Dataset, ItemDataset
│   │   │   └── alerta.py            # Alerta, RegraAlerta
│   │   │
│   │   ├── workers/                 # Celery tasks (background)
│   │   │   ├── worker_avaliacao.py  # Roda evals em background
│   │   │   ├── worker_analytics.py  # Calcula agregações por hora
│   │   │   └── worker_alerta.py     # Checa regras de alerta
│   │   │
│   │   └── bd/                      # Banco de dados
│   │       ├── sessao.py            # SQLAlchemy session
│   │       └── migracoes/           # Alembic migrations
│   │
│   └── testes/
│       ├── test_ingestao.py
│       ├── test_avaliadores.py
│       └── test_drift.py
│
├── dashboard/                       # 📊 Dashboard Streamlit
│   ├── app.py                       # Entry point
│   ├── paginas/
│   │   ├── visao_geral.py           # KPIs, scores médios, volume
│   │   ├── traces.py                # Explorador de traces
│   │   ├── avaliacoes.py            # Trends de scores ao longo do tempo
│   │   ├── comparacoes.py           # A/B de prompts e modelos
│   │   ├── datasets.py              # Gerenciar datasets de regressão
│   │   └── alertas.py               # Configurar e visualizar alertas
│   └── componentes/
│       ├── visualizador_trace.py    # Visualiza trace expandido
│       ├── cartao_score.py          # Card de score com trend
│       └── graficos.py              # Gráficos reutilizáveis
│
├── exemplos/                        # 🎯 Exemplos de integração
│   ├── vertice_ai/
│   │   ├── antes.py                 # Sem Sentinela
│   │   ├── depois.py                # Com Sentinela (3 linhas a mais)
│   │   └── README.md
│   ├── postador/
│   │   ├── antes.py
│   │   ├── depois.py
│   │   └── README.md
│   └── langchain_generico/
│       ├── exemplo.py
│       └── README.md
│
├── datasets/                        # 📋 Datasets de avaliação prontos
│   ├── vertice_ai_golden.json       # 50 perguntas + respostas esperadas
│   └── postador_golden.json         # 30 prompts + outputs esperados
│
├── docs/                            # 📖 Documentação
│   ├── arquitetura.md
│   ├── referencia_sdk.md
│   ├── avaliadores.md
│   ├── avaliadores_customizados.md
│   └── deploy.md
│
└── scripts/
    ├── popular_dados.py             # Popula com dados fake para demo
    └── rodar_benchmark.py           # Roda benchmark nos datasets
```

---

## Modelo de Dados

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────────┐
│   Projeto   │────▶│    Trace     │────▶│  ResultadoAvaliacao  │
│             │     │              │     │                      │
│ id          │     │ id           │     │ id                   │
│ nome        │     │ projeto_id   │     │ trace_id             │
│ api_key     │     │ input        │     │ avaliador            │
│ criado_em   │     │ output       │     │ score (0.0 - 1.0)    │
└─────────────┘     │ contexto     │     │ raciocinio           │
                    │ modelo       │     │ criado_em            │
                    │ tokens_entrada│    └──────────────────────┘
                    │ tokens_saida │
                    │ latencia_ms  │     ┌──────────────┐
                    │ custo_usd    │     │  RegraAlerta │
                    │ metadata     │     │              │
                    │ criado_em    │     │ avaliador    │
                    └──────────────┘     │ threshold    │
                                        │ janela_min   │
                    ┌──────────────┐     │ canal        │
                    │   Dataset    │     └──────────────┘
                    │              │
                    │ id           │
                    │ nome         │
                    │ itens[]      │
                    │  - input     │
                    │  - esperado  │
                    │  - contexto  │
                    └──────────────┘
```

---

## Casos de Uso Reais

- **Vértice AI**: detectou que 23% das respostas tinham baixa faithfulness — passavam despercebidas sem monitoramento
- **Postador**: identificou que trocar de GPT-4 para GPT-4o-mini reduziu custo em 60% sem perda mensurável de qualidade

---

## Roadmap

Veja o acompanhamento detalhado de features e progresso em [STATUS.md](STATUS.md).

---

## Documentação

- [Referência do SDK](docs/referencia_sdk.md)
- [Avaliadores customizados](docs/avaliadores_customizados.md)
- [Guia de deploy](docs/deploy.md)
- [Arquitetura](docs/arquitetura.md)

---

## Licença

MIT — use, modifique e distribua à vontade.
