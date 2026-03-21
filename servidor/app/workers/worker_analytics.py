"""Worker Celery de analytics — calcula agregações horárias."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger("sentinela.workers.analytics")


@celery_app.task(name="app.workers.worker_analytics.calcular_agregacoes")
def calcular_agregacoes() -> dict:
    """Calcula e armazena scores médios da última hora por projeto e avaliador."""
    return asyncio.run(_calcular_async())


async def _calcular_async() -> dict:
    from sqlalchemy import func, select

    from app.bd.sessao import FabricaSessao
    from app.modelos.trace import ResultadoAvaliacao, Trace

    janela_inicio = datetime.utcnow() - timedelta(hours=1)

    async with FabricaSessao() as sessao:
        consulta = (
            select(
                Trace.projeto,
                ResultadoAvaliacao.avaliador,
                func.avg(ResultadoAvaliacao.score).label("score_medio"),
                func.count(ResultadoAvaliacao.id).label("total"),
            )
            .join(ResultadoAvaliacao, ResultadoAvaliacao.trace_id == Trace.id)
            .where(Trace.criado_em >= janela_inicio)
            .group_by(Trace.projeto, ResultadoAvaliacao.avaliador)
        )
        resultado = await sessao.execute(consulta)
        linhas = resultado.all()

    agregacoes = [
        {
            "projeto": r.projeto,
            "avaliador": r.avaliador,
            "score_medio": round(float(r.score_medio), 4),
            "total": r.total,
        }
        for r in linhas
    ]

    logger.info("Agregações calculadas: %d grupos", len(agregacoes))
    return {"calculado_em": datetime.utcnow().isoformat(), "agregacoes": agregacoes}
