"""Esquemas Pydantic do servidor (espelham os modelos do SDK)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


def _novo_id() -> str:
    return str(uuid.uuid4())


class TraceEntrada(BaseModel):
    """Payload recebido do SDK via POST /traces."""

    id: str = Field(default_factory=_novo_id)
    projeto: str
    nome: str
    input: Optional[Any] = None
    output: Optional[Any] = None
    contexto: Optional[str] = None
    modelo: Optional[str] = None
    tokens_entrada: Optional[int] = None
    tokens_saida: Optional[int] = None
    latencia_ms: Optional[float] = None
    custo_usd: Optional[float] = None
    erro: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    criado_em: datetime = Field(default_factory=datetime.utcnow)


class AvaliacaoSaida(BaseModel):
    avaliador: str
    score: float
    aprovado: bool
    raciocinio: Optional[str] = None


class TraceSaida(BaseModel):
    id: str
    projeto: str
    nome: str
    input: Optional[Any] = None
    output: Optional[Any] = None
    contexto: Optional[str] = None
    modelo: Optional[str] = None
    tokens_entrada: Optional[int] = None
    tokens_saida: Optional[int] = None
    latencia_ms: Optional[float] = None
    custo_usd: Optional[float] = None
    erro: Optional[str] = None
    criado_em: Optional[str] = None
    avaliacoes: list[AvaliacaoSaida] = Field(default_factory=list)


class ListaTracesSaida(BaseModel):
    traces: list[TraceSaida]
    pagina: int
    limite: int
    total: int
