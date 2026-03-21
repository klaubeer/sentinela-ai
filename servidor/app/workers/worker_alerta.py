"""Worker Celery de alertas — checa regras e dispara notificações."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger("sentinela.workers.alerta")


@celery_app.task(name="app.workers.worker_alerta.verificar_alertas")
def verificar_alertas() -> dict:
    """Checa todas as regras de alerta ativas e dispara notificações se necessário."""
    return asyncio.run(_verificar_alertas_async())


async def _verificar_alertas_async() -> dict:
    from sqlalchemy import func, select

    from app.bd.sessao import FabricaSessao
    from app.modelos.alerta import Alerta, RegraAlerta
    from app.modelos.trace import ResultadoAvaliacao, Trace
    from app.nucleo.notificador import notificar_discord, notificar_slack

    disparados = 0

    async with FabricaSessao() as sessao:
        resultado = await sessao.execute(
            select(RegraAlerta).where(RegraAlerta.ativa == True)
        )
        regras = resultado.scalars().all()

        for regra in regras:
            janela_inicio = datetime.utcnow() - timedelta(minutes=regra.janela_minutos)

            # Score médio do avaliador na janela
            consulta = (
                select(func.avg(ResultadoAvaliacao.score))
                .join(Trace, Trace.id == ResultadoAvaliacao.trace_id)
                .where(
                    Trace.projeto == regra.projeto,
                    ResultadoAvaliacao.avaliador == regra.avaliador,
                    Trace.criado_em >= janela_inicio,
                )
            )
            score_medio = await sessao.scalar(consulta)

            if score_medio is None:
                continue  # sem dados na janela

            score_medio = float(score_medio)

            if score_medio >= regra.threshold:
                continue  # dentro do aceitável

            # Verifica se já foi alertado recentemente (evita spam)
            alerta_recente = await sessao.scalar(
                select(Alerta.id)
                .where(
                    Alerta.regra_id == regra.id,
                    Alerta.disparado_em >= janela_inicio,
                )
            )
            if alerta_recente:
                continue

            # Monta mensagem
            agora = datetime.utcnow()
            mensagem = {
                "projeto": regra.projeto,
                "avaliador": regra.avaliador,
                "score_medio": score_medio,
                "threshold": regra.threshold,
                "detalhe": (
                    f"Score médio de `{regra.avaliador}` caiu para `{score_medio:.2f}` "
                    f"(abaixo do threshold `{regra.threshold:.2f}`) "
                    f"nos últimos {regra.janela_minutos} minutos."
                ),
                "disparado_em": agora.strftime("%d/%m/%Y %H:%M UTC"),
            }

            # Dispara webhook
            enviado = False
            if regra.canal == "slack":
                enviado = await notificar_slack(regra.webhook_url, mensagem)
            elif regra.canal == "discord":
                enviado = await notificar_discord(regra.webhook_url, mensagem)

            if enviado:
                sessao.add(Alerta(
                    id=str(uuid.uuid4()),
                    regra_id=regra.id,
                    projeto=regra.projeto,
                    avaliador=regra.avaliador,
                    score_medio=score_medio,
                    threshold=regra.threshold,
                    mensagem=mensagem["detalhe"],
                    disparado_em=agora,
                ))
                disparados += 1
                logger.warning(
                    "Alerta disparado: projeto='%s' avaliador='%s' score=%.2f threshold=%.2f",
                    regra.projeto, regra.avaliador, score_medio, regra.threshold,
                )

        await sessao.commit()

    return {"verificado_em": datetime.utcnow().isoformat(), "alertas_disparados": disparados}
