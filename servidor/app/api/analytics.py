"""Endpoints de analytics — scores, volume e trends ao longo do tempo."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bd.sessao import obter_sessao
from app.modelos.trace import ResultadoAvaliacao, Trace

roteador = APIRouter(prefix="/analytics", tags=["Analytics"])


@roteador.get("/scores")
async def scores_por_avaliador(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    projeto: Optional[str] = Query(None),
    dias: int = Query(7, ge=1, le=90, description="Janela de tempo em dias"),
) -> dict:
    """Score médio por avaliador no período, com série temporal diária."""
    desde = datetime.utcnow() - timedelta(days=dias)

    # Score médio geral por avaliador
    consulta_media = (
        select(
            ResultadoAvaliacao.avaliador,
            func.avg(ResultadoAvaliacao.score).label("score_medio"),
            func.count(ResultadoAvaliacao.id).label("total"),
            func.sum(func.cast(ResultadoAvaliacao.aprovado, sqlalchemy_int())).label("aprovados"),
        )
        .join(Trace, Trace.id == ResultadoAvaliacao.trace_id)
        .where(Trace.criado_em >= desde)
    )
    if projeto:
        consulta_media = consulta_media.where(Trace.projeto == projeto)
    consulta_media = consulta_media.group_by(ResultadoAvaliacao.avaliador)

    resultado_media = await sessao.execute(consulta_media)
    medias = resultado_media.all()

    # Série temporal diária por avaliador
    consulta_serie = (
        select(
            func.date_trunc("day", Trace.criado_em).label("dia"),
            ResultadoAvaliacao.avaliador,
            func.avg(ResultadoAvaliacao.score).label("score_medio"),
            func.count(ResultadoAvaliacao.id).label("total"),
        )
        .join(Trace, Trace.id == ResultadoAvaliacao.trace_id)
        .where(Trace.criado_em >= desde)
    )
    if projeto:
        consulta_serie = consulta_serie.where(Trace.projeto == projeto)
    consulta_serie = consulta_serie.group_by("dia", ResultadoAvaliacao.avaliador).order_by("dia")

    resultado_serie = await sessao.execute(consulta_serie)
    serie = resultado_serie.all()

    return {
        "periodo_dias": dias,
        "desde": desde.isoformat(),
        "resumo": [
            {
                "avaliador": r.avaliador,
                "score_medio": round(float(r.score_medio), 4),
                "total": r.total,
                "aprovados": int(r.aprovados or 0),
                "taxa_aprovacao": round(int(r.aprovados or 0) / r.total, 4) if r.total else 0,
            }
            for r in medias
        ],
        "serie_temporal": [
            {
                "dia": r.dia.date().isoformat() if r.dia else None,
                "avaliador": r.avaliador,
                "score_medio": round(float(r.score_medio), 4),
                "total": r.total,
            }
            for r in serie
        ],
    }


@roteador.get("/volume")
async def volume_de_traces(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    projeto: Optional[str] = Query(None),
    dias: int = Query(7, ge=1, le=90),
) -> dict:
    """Volume de traces por dia e por projeto no período."""
    desde = datetime.utcnow() - timedelta(days=dias)

    consulta = (
        select(
            func.date_trunc("day", Trace.criado_em).label("dia"),
            Trace.projeto,
            func.count(Trace.id).label("total"),
            func.count(Trace.erro).label("com_erro"),
            func.avg(Trace.latencia_ms).label("latencia_media"),
        )
        .where(Trace.criado_em >= desde)
    )
    if projeto:
        consulta = consulta.where(Trace.projeto == projeto)
    consulta = consulta.group_by("dia", Trace.projeto).order_by("dia")

    resultado = await sessao.execute(consulta)
    linhas = resultado.all()

    return {
        "periodo_dias": dias,
        "serie": [
            {
                "dia": r.dia.date().isoformat() if r.dia else None,
                "projeto": r.projeto,
                "total": r.total,
                "com_erro": r.com_erro,
                "latencia_media_ms": round(float(r.latencia_media), 2) if r.latencia_media else None,
            }
            for r in linhas
        ],
    }


@roteador.get("/projetos")
async def resumo_por_projeto(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    dias: int = Query(7, ge=1, le=90),
) -> dict:
    """Resumo de métricas agrupado por projeto."""
    desde = datetime.utcnow() - timedelta(days=dias)

    consulta = (
        select(
            Trace.projeto,
            func.count(Trace.id).label("total_traces"),
            func.avg(Trace.latencia_ms).label("latencia_media"),
            func.sum(Trace.custo_usd).label("custo_total"),
            func.count(Trace.erro).label("total_erros"),
        )
        .where(Trace.criado_em >= desde)
        .group_by(Trace.projeto)
        .order_by(func.count(Trace.id).desc())
    )

    resultado = await sessao.execute(consulta)
    linhas = resultado.all()

    return {
        "periodo_dias": dias,
        "projetos": [
            {
                "projeto": r.projeto,
                "total_traces": r.total_traces,
                "latencia_media_ms": round(float(r.latencia_media), 2) if r.latencia_media else None,
                "custo_total_usd": round(float(r.custo_total), 6) if r.custo_total else 0.0,
                "total_erros": r.total_erros,
                "taxa_erro": round(r.total_erros / r.total_traces, 4) if r.total_traces else 0,
            }
            for r in linhas
        ],
    }


def sqlalchemy_int():
    from sqlalchemy import Integer
    return Integer
