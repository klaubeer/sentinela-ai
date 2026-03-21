"""Endpoint para listagem e consulta de traces."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.bd.sessao import obter_sessao
from app.modelos.trace import Trace

roteador = APIRouter(prefix="/traces", tags=["Traces"])


@roteador.get("")
async def listar_traces(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    projeto: Optional[str] = Query(None, description="Filtrar por projeto"),
    nome: Optional[str] = Query(None, description="Filtrar por nome da função"),
    com_erro: Optional[bool] = Query(None, description="Filtrar apenas traces com erro"),
    de: Optional[datetime] = Query(None, description="Data inicial (ISO 8601)"),
    ate: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),
    limite: int = Query(50, ge=1, le=500),
    pagina: int = Query(1, ge=1),
) -> dict:
    """Lista traces com filtros opcionais, paginados."""
    consulta = select(Trace).options(selectinload(Trace.resultados_avaliacao))

    if projeto:
        consulta = consulta.where(Trace.projeto == projeto)
    if nome:
        consulta = consulta.where(Trace.nome.ilike(f"%{nome}%"))
    if com_erro is True:
        consulta = consulta.where(Trace.erro.isnot(None))
    elif com_erro is False:
        consulta = consulta.where(Trace.erro.is_(None))
    if de:
        consulta = consulta.where(Trace.criado_em >= de)
    if ate:
        consulta = consulta.where(Trace.criado_em <= ate)

    total_consulta = select(Trace)
    if projeto:
        total_consulta = total_consulta.where(Trace.projeto == projeto)

    offset = (pagina - 1) * limite
    consulta = consulta.order_by(Trace.criado_em.desc()).offset(offset).limit(limite)

    resultado = await sessao.execute(consulta)
    traces = resultado.scalars().all()

    return {
        "traces": [_serializar_trace(t) for t in traces],
        "pagina": pagina,
        "limite": limite,
        "total": len(traces),
    }


@roteador.get("/{trace_id}")
async def obter_trace(
    trace_id: str,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> dict:
    """Retorna um trace específico com todos os resultados de avaliação."""
    resultado = await sessao.execute(
        select(Trace)
        .options(selectinload(Trace.resultados_avaliacao))
        .where(Trace.id == trace_id)
    )
    trace = resultado.scalar_one_or_none()

    if trace is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace não encontrado")

    return _serializar_trace(trace)


def _serializar_trace(trace: Trace) -> dict:
    return {
        "id": trace.id,
        "projeto": trace.projeto,
        "nome": trace.nome,
        "input": trace.input,
        "output": trace.output,
        "contexto": trace.contexto,
        "modelo": trace.modelo,
        "tokens_entrada": trace.tokens_entrada,
        "tokens_saida": trace.tokens_saida,
        "latencia_ms": trace.latencia_ms,
        "custo_usd": trace.custo_usd,
        "erro": trace.erro,
        "criado_em": trace.criado_em.isoformat() if trace.criado_em else None,
        "avaliacoes": [
            {
                "avaliador": r.avaliador,
                "score": r.score,
                "aprovado": r.aprovado,
                "raciocinio": r.raciocinio,
            }
            for r in trace.resultados_avaliacao
        ],
    }
