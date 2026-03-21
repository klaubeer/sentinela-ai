"""Endpoint de Drift Detection."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.bd.sessao import obter_sessao
from app.nucleo.detector_drift import DetectorDrift

roteador = APIRouter(prefix="/drift", tags=["Drift Detection"])


@roteador.get("/{projeto}")
async def analisar_drift(
    projeto: str,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    janela_horas: int = Query(24, ge=1, le=168, description="Tamanho da janela em horas"),
) -> dict:
    """Compara scores da janela atual com a anterior e retorna avaliadores em drift."""
    detector = DetectorDrift(sessao)
    relatorio = await detector.analisar(projeto=projeto, janela_horas=janela_horas)

    return {
        "projeto": relatorio.projeto,
        "tem_drift": relatorio.tem_drift,
        "janela_horas": janela_horas,
        "janela_atual_inicio": relatorio.janela_atual_inicio.isoformat(),
        "janela_anterior_inicio": relatorio.janela_anterior_inicio.isoformat(),
        "avaliadores_em_drift": len(relatorio.avaliadores_em_drift),
        "avaliadores": [
            {
                "avaliador": a.avaliador,
                "score_atual": a.score_atual,
                "score_anterior": a.score_anterior,
                "variacao": a.variacao,
                "variacao_pct": f"{a.variacao_pct * 100:+.1f}%",
                "tem_drift": a.tem_drift,
                "total_atual": a.total_atual,
                "total_anterior": a.total_anterior,
            }
            for a in relatorio.avaliadores
        ],
    }
