"""Vértice AI — DEPOIS do Sentinela.

Apenas 3 linhas adicionadas (marcadas com # <-- SENTINELA).
Todo o resto do código permanece idêntico.

O Sentinela passa a monitorar:
- Faithfulness (resposta é fiel ao contexto RAG?)
- Relevância (resposta responde à pergunta?)
- Latência de cada chamada
- Custo estimado por chamada
- Erros e exceções
"""

from sentinela import Sentinela, observe                          # <-- SENTINELA
from vertexai.generative_models import GenerativeModel
from minha_base_vetorial import recuperar_documentos

sentinela = Sentinela(api_key="sk-...", projeto="vertice-ai")     # <-- SENTINELA


@sentinela.observe(nome="responder-cliente")                      # <-- SENTINELA
def responder_cliente(pergunta: str) -> str:
    contexto = recuperar_documentos(pergunta)
    modelo = GenerativeModel("gemini-1.5-flash")
    resposta = modelo.generate_content(
        f"Contexto: {contexto}\n\nPergunta: {pergunta}"
    )
    return resposta.text


# Para monitorar também com guardrails (PII e toxicidade):
@sentinela.observe(
    nome="responder-cliente-seguro",
    # passa como metadata — o worker avalia no background
)
def responder_cliente_seguro(pergunta: str) -> str:
    contexto = recuperar_documentos(pergunta)
    modelo = GenerativeModel("gemini-1.5-flash")
    resposta = modelo.generate_content(
        f"Contexto: {contexto}\n\nPergunta: {pergunta}"
    )
    return resposta.text
