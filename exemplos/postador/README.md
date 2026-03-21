# Integração — Postador

## O que mudou

```diff
+ from sentinela import Sentinela, observe
  from openai import OpenAI

+ sentinela = Sentinela(api_key="sk-...", projeto="postador")

+ @sentinela.observe(nome="gerar-post")
  def gerar_post(briefing: str, tom: str = "profissional") -> str:
      ...
```

## Resultado real

O benchmark do Sentinela comparou `gpt-4o` vs `gpt-4o-mini` em 30 posts:

| Métrica | GPT-4o | GPT-4o-mini |
|---------|--------|-------------|
| Relevância | 0.91 | 0.89 |
| Coerência | 0.93 | 0.91 |
| Custo médio/post | $0.042 | $0.004 |

**Conclusão:** qualidade equivalente, **custo 90% menor**. Migração feita.
