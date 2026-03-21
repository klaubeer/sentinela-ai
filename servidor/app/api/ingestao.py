"""Endpoint de ingestão de traces enviados pelo SDK."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.bd.sessao import obter_sessao
from app.esquemas.trace import TraceEntrada
from app.modelos.trace import Trace as TraceORM
from app.nucleo.motor_avaliacao import MotorAvaliacao

logger = logging.getLogger("sentinela.api.ingestao")

roteador = APIRouter(prefix="/traces", tags=["Ingestão"])


@roteador.post("", status_code=status.HTTP_201_CREATED)
async def receber_trace(
    trace: TraceEntrada,
    tarefas_background: BackgroundTasks,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> dict:
    """Recebe um trace do SDK e agenda avaliação em background."""
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

    # Agenda avaliação em background sem bloquear a resposta
    motor = MotorAvaliacao(sessao)
    tarefas_background.add_task(motor.avaliar_trace, trace)

    return {"id": trace.id, "status": "recebido"}
