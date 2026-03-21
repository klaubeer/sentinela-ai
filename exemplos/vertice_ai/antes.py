"""Vértice AI — ANTES do Sentinela.

Código original sem nenhum monitoramento. Não há visibilidade sobre:
- Quantas respostas estão alucinando
- Latência por chamada
- Custo acumulado
- Qualidade das respostas ao longo do tempo
"""

from vertexai.generative_models import GenerativeModel
from minha_base_vetorial import recuperar_documentos  # seu RAG


def responder_cliente(pergunta: str) -> str:
    contexto = recuperar_documentos(pergunta)
    modelo = GenerativeModel("gemini-1.5-flash")
    resposta = modelo.generate_content(
        f"Contexto: {contexto}\n\nPergunta: {pergunta}"
    )
    return resposta.text
