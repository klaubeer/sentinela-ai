"""Avaliador Customizado — critério de avaliação definido pelo usuário via prompt."""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.configuracao import obter_configuracao
from app.esquemas.trace import TraceEntrada as Trace

from .base import AvaliadorBase, ResultadoAvaliador

logger = logging.getLogger("sentinela.avaliadores.customizado")

_PROMPT_WRAPPER = """Você é um avaliador de respostas de IA.

Critério de avaliação definido pelo usuário:
{criterio}

Responda SEMPRE com JSON válido no formato:
{{"score": <número entre 0.0 e 1.0>, "raciocinio": "<explicação curta em português>"}}

Input do usuário:
{input}

Resposta gerada:
{output}

Aplique o critério e retorne o score."""


class AvaliadorCustomizado(AvaliadorBase):
    """Avaliador que permite ao usuário definir qualquer critério via prompt em linguagem natural.

    Uso:
        avaliador = AvaliadorCustomizado(
            nome="tom-formal",
            criterio="A resposta mantém um tom formal e profissional?",
            threshold=0.8,
        )
    """

    def __init__(
        self,
        nome: str,
        criterio: str,
        threshold: float = 0.7,
    ) -> None:
        self.nome = nome
        self.descricao = criterio
        self.threshold = threshold
        config = obter_configuracao()
        self._llm = AsyncOpenAI(api_key=config.openai_api_key)
        self._modelo = config.modelo_avaliacao
        self._criterio = criterio

    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        if not trace.output:
            return self._resultado(score=1.0, raciocinio="Sem output para avaliar")

        try:
            prompt = _PROMPT_WRAPPER.format(
                criterio=self._criterio,
                input=str(trace.input or "N/A"),
                output=str(trace.output),
            )
            resposta = await self._llm.chat.completions.create(
                model=self._modelo,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
            )
            dados = json.loads(resposta.choices[0].message.content or "{}")
            return self._resultado(
                score=float(dados.get("score", 0.5)),
                raciocinio=dados.get("raciocinio", ""),
            )
        except Exception as e:
            logger.warning("Erro no avaliador customizado '%s' para trace %s: %s", self.nome, trace.id, e)
            return self._resultado(score=0.5, raciocinio=f"Erro na avaliação: {e}")
