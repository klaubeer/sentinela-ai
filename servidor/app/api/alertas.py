"""CRUD de regras de alerta e histórico de disparos."""

from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bd.sessao import obter_sessao
from app.modelos.alerta import Alerta, RegraAlerta

roteador = APIRouter(prefix="/alertas", tags=["Alertas"])


class RegraEntrada(BaseModel):
    nome: str
    projeto: str
    avaliador: str
    threshold: float = Field(ge=0.0, le=1.0)
    janela_minutos: int = Field(default=60, ge=5, le=1440)
    canal: str = Field(default="slack", pattern="^(slack|discord)$")
    webhook_url: str


@roteador.post("/regras", status_code=status.HTTP_201_CREATED)
async def criar_regra(
    dados: RegraEntrada,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> dict:
    regra = RegraAlerta(
        id=str(uuid.uuid4()),
        nome=dados.nome,
        projeto=dados.projeto,
        avaliador=dados.avaliador,
        threshold=dados.threshold,
        janela_minutos=dados.janela_minutos,
        canal=dados.canal,
        webhook_url=dados.webhook_url,
    )
    sessao.add(regra)
    await sessao.commit()
    return {"id": regra.id, "nome": regra.nome, "status": "criada"}


@roteador.get("/regras")
async def listar_regras(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    projeto: Optional[str] = None,
) -> list[dict]:
    consulta = select(RegraAlerta)
    if projeto:
        consulta = consulta.where(RegraAlerta.projeto == projeto)
    resultado = await sessao.execute(consulta.order_by(RegraAlerta.criado_em.desc()))
    regras = resultado.scalars().all()
    return [_serializar_regra(r) for r in regras]


@roteador.delete("/regras/{regra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_regra(
    regra_id: str,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> None:
    resultado = await sessao.execute(select(RegraAlerta).where(RegraAlerta.id == regra_id))
    regra = resultado.scalar_one_or_none()
    if not regra:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    await sessao.delete(regra)
    await sessao.commit()


@roteador.get("/historico")
async def historico_alertas(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    projeto: Optional[str] = None,
    limite: int = 50,
) -> list[dict]:
    consulta = select(Alerta)
    if projeto:
        consulta = consulta.where(Alerta.projeto == projeto)
    consulta = consulta.order_by(Alerta.disparado_em.desc()).limit(limite)
    resultado = await sessao.execute(consulta)
    alertas = resultado.scalars().all()
    return [
        {
            "id": a.id,
            "regra_id": a.regra_id,
            "projeto": a.projeto,
            "avaliador": a.avaliador,
            "score_medio": a.score_medio,
            "threshold": a.threshold,
            "mensagem": a.mensagem,
            "disparado_em": a.disparado_em.isoformat(),
        }
        for a in alertas
    ]


def _serializar_regra(r: RegraAlerta) -> dict:
    return {
        "id": r.id,
        "nome": r.nome,
        "projeto": r.projeto,
        "avaliador": r.avaliador,
        "threshold": r.threshold,
        "janela_minutos": r.janela_minutos,
        "canal": r.canal,
        "ativa": r.ativa,
        "criado_em": r.criado_em.isoformat(),
    }
