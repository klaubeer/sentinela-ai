"""Avaliador de Relevância — verifica se a resposta responde à pergunta do usuário."""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.configuracao import obter_configuracao
from app.esquemas.trace import TraceEntrada as Trace

from .base import AvaliadorBase, ResultadoAvaliador

logger = logging.getLogger("sentinela.avaliadores.relevancia")

PROMPT_SISTEMA = """Você é um avaliador especializado em qualidade de respostas de IA.
Sua tarefa é verificar se a resposta gerada é relevante e realmente responde à pergunta feita.

Responda SEMPRE com JSON válido no formato:
{"score": <número entre 0.0 e 1.0>, "raciocinio": "<explicação curta em português>"}

Critérios de score:
- 1.0: Resposta direta, completa e perfeitamente alinhada à pergunta
- 0.7-0.9: Responde bem mas poderia ser mais direta ou completa
- 0.4-0.6: Parcialmente relevante, desvia do ponto principal
- 0.0-0.3: Resposta fora do assunto ou completamente inadequada"""

PROMPT_USUARIO = """Pergunta do usuário:
{input}

Resposta gerada:
{output}

Avalie se a resposta é relevante e responde à pergunta."""


class AvaliadorRelevancia(AvaliadorBase):
    nome = "relevancia"
    descricao = "Verifica se a resposta realmente responde à pergunta do usuário"
    threshold = 0.7

    def __init__(self) -> None:
        config = obter_configuracao()
        self._llm = AsyncOpenAI(api_key=config.openai_api_key)
        self._modelo = config.modelo_avaliacao

    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        if not trace.input or not trace.output:
            logger.debug("Trace %s sem input ou output — pulando relevância", trace.id)
            return self._resultado(score=1.0, raciocinio="Sem dados suficientes para avaliar")

        try:
            resposta = await self._llm.chat.completions.create(
                model=self._modelo,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {
                        "role": "user",
                        "content": PROMPT_USUARIO.format(
                            input=str(trace.input),
                            output=str(trace.output),
                        ),
                    },
                ],
            )
            conteudo = resposta.choices[0].message.content or "{}"
            dados = json.loads(conteudo)
            score = float(dados.get("score", 0.5))
            raciocinio = dados.get("raciocinio", "")
            return self._resultado(score=score, raciocinio=raciocinio)

        except Exception as e:
            logger.warning("Erro ao avaliar relevância para trace %s: %s", trace.id, e)
            return self._resultado(score=0.5, raciocinio=f"Erro na avaliação: {e}")
