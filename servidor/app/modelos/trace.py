"""Models SQLAlchemy para traces e resultados de avaliação."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.bd.sessao import Base


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    projeto: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    input: Mapped[Optional[Any]] = mapped_column(JSONB)
    output: Mapped[Optional[Any]] = mapped_column(JSONB)
    contexto: Mapped[Optional[str]] = mapped_column(Text)
    modelo: Mapped[Optional[str]] = mapped_column(String(100))
    tokens_entrada: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_saida: Mapped[Optional[int]] = mapped_column(Integer)
    latencia_ms: Mapped[Optional[float]] = mapped_column(Float)
    custo_usd: Mapped[Optional[float]] = mapped_column(Float)
    erro: Mapped[Optional[str]] = mapped_column(Text)
    metadata_extra: Mapped[Optional[Any]] = mapped_column(JSONB, name="metadata")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    resultados_avaliacao: Mapped[list["ResultadoAvaliacao"]] = relationship(
        back_populates="trace", cascade="all, delete-orphan"
    )


class ResultadoAvaliacao(Base):
    __tablename__ = "resultados_avaliacao"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str] = mapped_column(ForeignKey("traces.id", ondelete="CASCADE"), index=True)
    avaliador: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    aprovado: Mapped[bool] = mapped_column(default=True)
    raciocinio: Mapped[Optional[str]] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    trace: Mapped["Trace"] = relationship(back_populates="resultados_avaliacao")
