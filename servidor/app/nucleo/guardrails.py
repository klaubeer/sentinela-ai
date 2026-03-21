"""Guardrails — avalia respostas e registra flags de violação no trace."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.avaliadores.deteccao_pii import AvaliadorDeteccaoPII
from app.avaliadores.toxicidade import AvaliadorToxicidade
from app.esquemas.trace import TraceEntrada as Trace

logger = logging.getLogger("sentinela.nucleo.guardrails")


@dataclass
class ResultadoGuardrail:
    passou: bool
    violacoes: list[str] = field(default_factory=list)
    detalhes: dict[str, str] = field(default_factory=dict)


# Mapa de nome → avaliador para os guardrails disponíveis
_GUARDRAILS_DISPONIVEIS = {
    "sem_pii": AvaliadorDeteccaoPII,
    "sem_toxicidade": AvaliadorToxicidade,
}


class MotorGuardrails:
    """Roda guardrails selecionados em um trace e retorna as violações encontradas.

    Não bloqueia — apenas avalia, registra e retorna o resultado para o caller
    decidir o que fazer (logar, alertar, etc.).
    """

    def __init__(self, guardrails: list[str]) -> None:
        self._avaliadores = []
        for nome in guardrails:
            cls = _GUARDRAILS_DISPONIVEIS.get(nome)
            if cls is None:
                logger.warning("Guardrail desconhecido ignorado: '%s'", nome)
                continue
            self._avaliadores.append((nome, cls()))

    async def verificar(self, trace: Trace) -> ResultadoGuardrail:
        """Roda todos os guardrails e retorna as violações encontradas."""
        violacoes: list[str] = []
        detalhes: dict[str, str] = {}

        for nome, avaliador in self._avaliadores:
            try:
                resultado = await avaliador.avaliar(trace)
                if not resultado.aprovado:
                    violacoes.append(nome)
                    detalhes[nome] = resultado.raciocinio or "violação detectada"
                    logger.warning(
                        "Guardrail '%s' violado no trace %s (score=%.2f): %s",
                        nome,
                        trace.id,
                        resultado.score,
                        resultado.raciocinio,
                    )
            except Exception as e:
                logger.error("Erro ao rodar guardrail '%s': %s", nome, e)

        return ResultadoGuardrail(
            passou=len(violacoes) == 0,
            violacoes=violacoes,
            detalhes=detalhes,
        )
