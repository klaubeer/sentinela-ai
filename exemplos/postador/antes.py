"""Postador — ANTES do Sentinela.

Geração de posts sem visibilidade sobre qualidade, custo ou toxicidade.
"""

from openai import OpenAI

cliente = OpenAI()


def gerar_post(briefing: str, tom: str = "profissional") -> str:
    resposta = cliente.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"Você é um copywriter especialista. Tom: {tom}.",
            },
            {"role": "user", "content": f"Crie um post para LinkedIn:\n{briefing}"},
        ],
    )
    return resposta.choices[0].message.content
