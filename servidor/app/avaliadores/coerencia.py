"""Avaliador de Coerência — verifica se a resposta é coerente e bem estruturada."""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.configuracao import obter_configuracao
from app.esquemas.trace import TraceEntrada as Trace

from .base import AvaliadorBase, ResultadoAvaliador

logger = logging.getLogger("sentinela.avaliadores.coerencia")

PROMPT_SISTEMA = """Você é um avaliador especializado em qualidade textual de respostas de IA.
Avalie se a resposta é coerente, bem estruturada, gramaticalmente correta e fácil de entender.

Responda SEMPRE com JSON válido no formato:
{"score": <número entre 0.0 e 1.0>, "raciocinio": "<explicação curta em português>"}

Critérios de score:
- 1.0: Resposta clara, bem estruturada, fluente e sem contradições
- 0.7-0.9: Boa coerência com pequenos problemas de estrutura ou fluidez
- 0.4-0.6: Parcialmente coerente, com alguns trechos confusos ou contraditórios
- 0.0-0.3: Incoerente, confusa, contraditória ou incompreensível"""

PROMPT_USUARIO = """Resposta gerada:
{output}

Avalie a coerência e qualidade textual da resposta."""


class AvaliadorCoerencia(AvaliadorBase):
    nome = "coerencia"
    descricao = "Verifica se a resposta é coerente, bem estruturada e fácil de entender"
    threshold = 0.7

    def __init__(self) -> None:
        config = obter_configuracao()
        self._llm = AsyncOpenAI(api_key=config.openai_api_key)
        self._modelo = config.modelo_avaliacao

    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        if not trace.output:
            return self._resultado(score=1.0, raciocinio="Sem output para avaliar")

        try:
            resposta = await self._llm.chat.completions.create(
                model=self._modelo,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": PROMPT_USUARIO.format(output=str(trace.output))},
                ],
            )
            dados = json.loads(resposta.choices[0].message.content or "{}")
            return self._resultado(
                score=float(dados.get("score", 0.5)),
                raciocinio=dados.get("raciocinio", ""),
            )
        except Exception as e:
            logger.warning("Erro ao avaliar coerência para trace %s: %s", trace.id, e)
            return self._resultado(score=0.5, raciocinio=f"Erro na avaliação: {e}")
