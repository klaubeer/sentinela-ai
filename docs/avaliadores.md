# Avaliadores

Todos os avaliadores retornam um score entre **0.0 e 1.0** e um campo `raciocinio` explicando a nota.

Score >= threshold → `aprovado: true`. Threshold padrão: **0.7**.

---

## Faithfulness

**Arquivo:** `servidor/app/avaliadores/faithfulness.py`
**Tipo:** LLM-as-Judge (GPT-4o-mini)
**Threshold:** 0.7

Verifica se a resposta está fundamentada no contexto recuperado pelo RAG. Detecta alucinações — informações que o modelo inventou sem base no contexto.

Só roda se o trace tiver campo `contexto` preenchido.

---

## Relevância

**Arquivo:** `servidor/app/avaliadores/relevancia.py`
**Tipo:** LLM-as-Judge
**Threshold:** 0.7

Verifica se a resposta realmente responde à pergunta feita. Uma resposta pode ser factualmente correta mas completamente fora do ponto.

---

## Toxicidade

**Arquivo:** `servidor/app/avaliadores/toxicidade.py`
**Tipo:** LLM-as-Judge
**Threshold:** 0.7

Score **alto = conteúdo seguro**. Detecta linguagem ofensiva, discriminatória, violenta ou sexualmente explícita.

---

## Coerência

**Arquivo:** `servidor/app/avaliadores/coerencia.py`
**Tipo:** LLM-as-Judge
**Threshold:** 0.7

Avalia se a resposta é bem estruturada, fluente e sem contradições internas. Independente de ser correta ou relevante.

---

## Detecção de PII

**Arquivo:** `servidor/app/avaliadores/deteccao_pii.py`
**Tipo:** Regex (sem LLM)
**Threshold:** 0.8

Detecta dados pessoais vazados na resposta. Score **alto = sem PII**.

Padrões detectados: CPF, CNPJ, RG, telefone BR, e-mail, número de cartão de crédito, CEP.

Threshold mais rigoroso (0.8) pois PII em resposta é risco alto.

---

## Eficiência de Custo

**Arquivo:** `servidor/app/avaliadores/eficiencia_custo.py`
**Tipo:** Heurística (sem LLM)
**Threshold:** 0.5

Avalia o custo por trace com base em tokens e modelo. Usa tabela de preços atualizada por modelo.

| Score | Custo por trace |
|-------|----------------|
| 1.0 | < $0.001 |
| 0.7–0.9 | $0.001 – $0.01 |
| 0.3–0.7 | $0.01 – $0.05 |
| 0.1 | > $0.05 |

---

## Customizado

**Arquivo:** `servidor/app/avaliadores/customizado.py`
**Tipo:** LLM-as-Judge com critério do usuário
**Threshold:** configurável

```python
from app.avaliadores.customizado import AvaliadorCustomizado

avaliador = AvaliadorCustomizado(
    nome="tom-formal",
    criterio="A resposta mantém um tom formal e profissional, sem gírias?",
    threshold=0.8,
)
```

Veja o guia completo em [avaliadores_customizados.md](avaliadores_customizados.md).
