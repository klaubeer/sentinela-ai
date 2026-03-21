"""ORM models para Dataset e ItemDataset."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.bd.sessao import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    projeto: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    itens: Mapped[list["ItemDataset"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class ItemDataset(Base):
    __tablename__ = "itens_dataset"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    input: Mapped[Any] = mapped_column(JSONB, nullable=False)
    output_esperado: Mapped[Optional[Any]] = mapped_column(JSONB)
    contexto: Mapped[Optional[str]] = mapped_column(Text)
    metadata_extra: Mapped[Optional[Any]] = mapped_column(JSONB, name="metadata")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="itens")
