"""Postador — DEPOIS do Sentinela.

3 linhas adicionadas. Passa a monitorar qualidade, custo e toxicidade de cada post gerado.
"""

from sentinela import Sentinela, observe                           # <-- SENTINELA
from openai import OpenAI

sentinela = Sentinela(api_key="sk-...", projeto="postador")        # <-- SENTINELA
cliente = OpenAI()


@sentinela.observe(nome="gerar-post")                             # <-- SENTINELA
def gerar_post(briefing: str, tom: str = "profissional") -> str:
    resposta = cliente.chat.completions.create(
        model="gpt-4o-mini",   # trocado após benchmark mostrar equivalência com gpt-4o
        messages=[
            {
                "role": "system",
                "content": f"Você é um copywriter especialista. Tom: {tom}.",
            },
            {"role": "user", "content": f"Crie um post para LinkedIn:\n{briefing}"},
        ],
    )
    return resposta.choices[0].message.content
