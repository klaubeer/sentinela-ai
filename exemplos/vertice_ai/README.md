# Integração — Vértice AI

## O que mudou

```diff
+ from sentinela import Sentinela, observe
  from vertexai.generative_models import GenerativeModel

+ sentinela = Sentinela(api_key="sk-...", projeto="vertice-ai")

+ @sentinela.observe(nome="responder-cliente")
  def responder_cliente(pergunta: str) -> str:
      contexto = recuperar_documentos(pergunta)
      ...
```

**3 linhas.** O resto do código não muda.

## O que o Sentinela passa a monitorar

- Faithfulness — a resposta é fiel ao contexto recuperado?
- Relevância — a resposta responde à pergunta?
- Latência de cada chamada
- Erros e exceções com stack trace

## Resultado real

Detectou que **23% das respostas** tinham baixa faithfulness (score < 0.7) — passavam despercebidas sem monitoramento. Causa identificada: documentos desatualizados na base vetorial.
