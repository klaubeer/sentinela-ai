"""Endpoint de ingestão de traces enviados pelo SDK."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.bd.sessao import obter_sessao
from app.esquemas.trace import TraceEntrada
from app.modelos.trace import Trace as TraceORM

logger = logging.getLogger("sentinela.api.ingestao")

roteador = APIRouter(prefix="/traces", tags=["Ingestão"])


@roteador.post("", status_code=status.HTTP_201_CREATED)
async def receber_trace(
    trace: TraceEntrada,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    background_tasks: BackgroundTasks,
) -> dict:
    """Recebe um trace do SDK, persiste no banco e dispara avaliação em background."""
    orm = TraceORM(
        id=trace.id,
        projeto=trace.projeto,
        nome=trace.nome,
        input=trace.input,
        output=trace.output,
        contexto=trace.contexto,
        modelo=trace.modelo,
        tokens_entrada=trace.tokens_entrada,
        tokens_saida=trace.tokens_saida,
        latencia_ms=trace.latencia_ms,
        custo_usd=trace.custo_usd,
        erro=trace.erro,
        metadata_extra=trace.metadata,
        criado_em=trace.criado_em,
    )

    sessao.add(orm)
    await sessao.commit()

    logger.info("Trace recebido: %s (projeto=%s, nome=%s)", trace.id, trace.projeto, trace.nome)

    # Avalia em background sem depender do Celery broker
    from app.workers.worker_avaliacao import _avaliar_trace_async
    background_tasks.add_task(_avaliar_trace_async, trace.model_dump(mode="json"))

    return {"id": trace.id, "status": "recebido"}
