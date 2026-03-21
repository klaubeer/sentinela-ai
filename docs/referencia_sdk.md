# Referência do SDK

## Instalação

```bash
pip install sentinela-ai

# Com suporte a LangChain:
pip install sentinela-ai[langchain]
```

## Inicialização

```python
from sentinela import Sentinela

sentinela = Sentinela(
    api_key="sk-...",           # obrigatório
    projeto="meu-projeto",      # obrigatório — agrupa traces no dashboard
    base_url="http://localhost:8000",  # padrão
)
```

## `@observe()` — Decorator

Instrumenta qualquer função Python, síncrona ou assíncrona.

```python
@sentinela.observe(
    nome="nome-da-operacao",    # opcional — padrão: nome da função
    capturar_input=True,        # padrão: True
    capturar_output=True,       # padrão: True
)
def minha_funcao(pergunta: str) -> str:
    ...
```

### O que é capturado automaticamente

| Campo | Descrição |
|-------|-----------|
| `input` | Argumentos da função |
| `output` | Valor retornado |
| `latencia_ms` | Tempo de execução em milissegundos |
| `erro` | Exceção lançada (se houver) — a exceção ainda é relançada |
| `criado_em` | Timestamp UTC do início da execução |

### Campos enriquecidos manualmente

Para passar informações adicionais (contexto RAG, modelo, tokens), use metadados no retorno ou instrumente manualmente via `SentinelaCliente`.

## `SentinelaCallbackHandler` — LangChain

```python
from sentinela.integracoes.langchain import SentinelaCallbackHandler

handler = SentinelaCallbackHandler()

# Qualquer chain, agent ou LLM do LangChain
chain.invoke(input, config={"callbacks": [handler]})
```

Captura automaticamente: prompt, resposta, modelo, tokens e latência.

## Guardrails via Metadata

```python
@sentinela.observe(nome="atendimento")
def atender(pergunta: str) -> str:
    ...

# Para ativar guardrails, passe nos metadados do trace:
# (via SDK avançado ou direto na API)
trace_com_guardrail = {
    ...,
    "metadata": {"guardrails": ["sem_pii", "sem_toxicidade"]}
}
```

## Comportamento em falhas

- Servidor indisponível → trace descartado silenciosamente, sua função continua
- Timeout de rede → idem
- Exceção na função → capturada no campo `erro`, exceção relançada normalmente
