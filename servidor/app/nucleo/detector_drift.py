"""Detector de Drift — compara janelas de tempo e identifica degradação de qualidade."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.trace import ResultadoAvaliacao, Trace

logger = logging.getLogger("sentinela.nucleo.detector_drift")

# Queda mínima no score para ser considerada drift
THRESHOLD_DRIFT = 0.10


@dataclass
class DriftAvaliador:
    avaliador: str
    score_atual: float
    score_anterior: float
    variacao: float          # negativo = piora
    variacao_pct: float
    tem_drift: bool
    total_atual: int
    total_anterior: int


@dataclass
class RelatorioDrift:
    projeto: str
    janela_atual_inicio: datetime
    janela_anterior_inicio: datetime
    avaliadores: list[DriftAvaliador] = field(default_factory=list)

    @property
    def tem_drift(self) -> bool:
        return any(a.tem_drift for a in self.avaliadores)

    @property
    def avaliadores_em_drift(self) -> list[DriftAvaliador]:
        return [a for a in self.avaliadores if a.tem_drift]


class DetectorDrift:
    """Compara scores médios entre duas janelas de tempo consecutivas.

    Janela atual  = últimas N horas
    Janela anterior = N horas antes disso
    """

    def __init__(self, sessao: AsyncSession) -> None:
        self._sessao = sessao

    async def analisar(
        self,
        projeto: str,
        janela_horas: int = 24,
    ) -> RelatorioDrift:
        agora = datetime.utcnow()
        janela_atual_inicio = agora - timedelta(hours=janela_horas)
        janela_anterior_inicio = janela_atual_inicio - timedelta(hours=janela_horas)

        scores_atual = await self._scores_por_avaliador(
            projeto, janela_atual_inicio, agora
        )
        scores_anterior = await self._scores_por_avaliador(
            projeto, janela_anterior_inicio, janela_atual_inicio
        )

        avaliadores = []
        for avaliador, (score_atual, total_atual) in scores_atual.items():
            if avaliador not in scores_anterior:
                continue

            score_anterior, total_anterior = scores_anterior[avaliador]
            variacao = score_atual - score_anterior
            variacao_pct = variacao / score_anterior if score_anterior > 0 else 0.0
            tem_drift = variacao < -THRESHOLD_DRIFT

            avaliadores.append(DriftAvaliador(
                avaliador=avaliador,
                score_atual=round(score_atual, 4),
                score_anterior=round(score_anterior, 4),
                variacao=round(variacao, 4),
                variacao_pct=round(variacao_pct, 4),
                tem_drift=tem_drift,
                total_atual=total_atual,
                total_anterior=total_anterior,
            ))

            if tem_drift:
                logger.warning(
                    "Drift detectado em '%s' — avaliador '%s': %.2f → %.2f (%.1f%%)",
                    projeto,
                    avaliador,
                    score_anterior,
                    score_atual,
                    variacao_pct * 100,
                )

        return RelatorioDrift(
            projeto=projeto,
            janela_atual_inicio=janela_atual_inicio,
            janela_anterior_inicio=janela_anterior_inicio,
            avaliadores=sorted(avaliadores, key=lambda a: a.variacao),
        )

    async def _scores_por_avaliador(
        self,
        projeto: str,
        inicio: datetime,
        fim: datetime,
    ) -> dict[str, tuple[float, int]]:
        """Retorna {avaliador: (score_medio, total)} para a janela de tempo."""
        consulta = (
            select(
                ResultadoAvaliacao.avaliador,
                func.avg(ResultadoAvaliacao.score).label("score_medio"),
                func.count(ResultadoAvaliacao.id).label("total"),
            )
            .join(Trace, Trace.id == ResultadoAvaliacao.trace_id)
            .where(
                Trace.projeto == projeto,
                Trace.criado_em >= inicio,
                Trace.criado_em < fim,
                # Exclui resultados de guardrail (prefixo "guardrail:")
                ~ResultadoAvaliacao.avaliador.startswith("guardrail:"),
            )
            .group_by(ResultadoAvaliacao.avaliador)
        )
        resultado = await self._sessao.execute(consulta)
        return {
            r.avaliador: (float(r.score_medio), r.total)
            for r in resultado.all()
        }
