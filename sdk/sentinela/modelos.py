"""Modelos Pydantic compartilhados entre SDK e servidor."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


def _novo_id() -> str:
    return str(uuid.uuid4())


class Span(BaseModel):
    """Representa uma operação interna dentro de um trace (ex: chamada ao LLM, busca no vetor store)."""

    id: str = Field(default_factory=_novo_id)
    nome: str
    inicio: datetime = Field(default_factory=datetime.utcnow)
    fim: Optional[datetime] = None
    latencia_ms: Optional[float] = None
    tipo: Optional[str] = None  # "llm", "retrieval", "tool", etc.
    metadata: dict[str, Any] = Field(default_factory=dict)


class Trace(BaseModel):
    """Representa uma interação completa com um sistema LLM."""

    id: str = Field(default_factory=_novo_id)
    projeto: str
    nome: str
    input: Any
    output: Optional[Any] = None
    contexto: Optional[str] = None  # conteúdo RAG recuperado
    modelo: Optional[str] = None
    tokens_entrada: Optional[int] = None
    tokens_saida: Optional[int] = None
    latencia_ms: Optional[float] = None
    custo_usd: Optional[float] = None
    erro: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    spans: list[Span] = Field(default_factory=list)
    criado_em: datetime = Field(default_factory=datetime.utcnow)


class ResultadoAvaliacao(BaseModel):
    """Score retornado por um avaliador para um trace específico."""

    id: str = Field(default_factory=_novo_id)
    trace_id: str
    avaliador: str
    score: float  # 0.0 a 1.0
    aprovado: bool
    raciocinio: Optional[str] = None
    criado_em: datetime = Field(default_factory=datetime.utcnow)
