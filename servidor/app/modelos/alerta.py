"""ORM models para RegraAlerta e Alerta (histórico de disparos)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.bd.sessao import Base


class RegraAlerta(Base):
    __tablename__ = "regras_alerta"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    projeto: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    avaliador: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    janela_minutos: Mapped[int] = mapped_column(Integer, default=60)
    canal: Mapped[str] = mapped_column(String(20), default="slack")  # "slack" | "discord"
    webhook_url: Mapped[str] = mapped_column(Text, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Alerta(Base):
    """Histórico de alertas disparados."""

    __tablename__ = "alertas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    regra_id: Mapped[str] = mapped_column(String(36), index=True)
    projeto: Mapped[str] = mapped_column(String(100))
    avaliador: Mapped[str] = mapped_column(String(100))
    score_medio: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    mensagem: Mapped[str] = mapped_column(Text)
    disparado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
