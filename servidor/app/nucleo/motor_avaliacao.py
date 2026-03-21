"""Motor de avaliação — orquestra os avaliadores para um trace."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.avaliadores.base import AvaliadorBase
from app.avaliadores.faithfulness import AvaliadorFaithfulness
from app.avaliadores.relevancia import AvaliadorRelevancia
from app.esquemas.trace import TraceEntrada
from app.modelos.trace import ResultadoAvaliacao

logger = logging.getLogger("sentinela.nucleo.motor_avaliacao")

# Avaliadores ativos na Fase 1
AVALIADORES_PADRAO: list[AvaliadorBase] = [
    AvaliadorFaithfulness(),
    AvaliadorRelevancia(),
]


class MotorAvaliacao:
    """Roda todos os avaliadores configurados para um trace e persiste os resultados."""

    def __init__(
        self,
        sessao: AsyncSession,
        avaliadores: list[AvaliadorBase] | None = None,
    ) -> None:
        self._sessao = sessao
        self._avaliadores = avaliadores or AVALIADORES_PADRAO

    async def avaliar_trace(self, trace: TraceEntrada) -> None:
        """Avalia um trace com todos os avaliadores e salva os resultados no banco."""
        for avaliador in self._avaliadores:
            try:
                resultado = await avaliador.avaliar(trace)
                orm = ResultadoAvaliacao(
                    id=resultado.avaliador + "_" + trace.id,
                    trace_id=trace.id,
                    avaliador=resultado.avaliador,
                    score=resultado.score,
                    aprovado=resultado.aprovado,
                    raciocinio=resultado.raciocinio,
                )
                self._sessao.add(orm)
                logger.info(
                    "Trace %s — %s: %.2f (%s)",
                    trace.id,
                    resultado.avaliador,
                    resultado.score,
                    "✓" if resultado.aprovado else "✗",
                )
            except Exception as e:
                logger.error(
                    "Falha ao rodar avaliador %s para trace %s: %s",
                    avaliador.nome,
                    trace.id,
                    e,
                )

        await self._sessao.commit()
