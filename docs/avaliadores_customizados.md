# Avaliadores Customizados

## Opção 1 — Via `AvaliadorCustomizado` (sem código)

A forma mais rápida: defina o critério em linguagem natural.

```python
from app.avaliadores.customizado import AvaliadorCustomizado

avaliador = AvaliadorCustomizado(
    nome="tom-formal",
    criterio="A resposta mantém um tom formal e profissional, sem gírias ou informalidades?",
    threshold=0.8,
)
```

Adicione ao worker em `worker_avaliacao.py`:

```python
avaliadores = [
    AvaliadorFaithfulness(),
    AvaliadorRelevancia(),
    AvaliadorCustomizado(
        nome="tom-formal",
        criterio="A resposta é formal e profissional?",
    ),
]
```

## Opção 2 — Subclasse de `AvaliadorBase` (controle total)

Para lógica mais complexa, implemente a interface:

```python
from app.avaliadores.base import AvaliadorBase, ResultadoAvaliador
from app.esquemas.trace import TraceEntrada as Trace


class AvaliadorComprimento(AvaliadorBase):
    nome = "comprimento-ideal"
    descricao = "Resposta tem entre 50 e 300 palavras?"
    threshold = 0.8

    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        if not trace.output:
            return self._resultado(score=1.0, raciocinio="Sem output")

        palavras = len(str(trace.output).split())

        if 50 <= palavras <= 300:
            return self._resultado(score=1.0, raciocinio=f"{palavras} palavras — ideal")
        elif palavras < 50:
            score = palavras / 50
            return self._resultado(score=score, raciocinio=f"Resposta curta: {palavras} palavras")
        else:
            score = max(0.3, 300 / palavras)
            return self._resultado(score=score, raciocinio=f"Resposta longa: {palavras} palavras")
```

## Boas práticas

- Prompts de critério devem ser específicos — "a resposta é boa?" é vago demais
- Use `threshold=0.8` ou acima para critérios de compliance
- Para critérios binários (passou/não passou), use score 0.0 ou 1.0 explicitamente
- Avaliadores sem LLM (regex, heurística) são mais rápidos e gratuitos — prefira quando possível
