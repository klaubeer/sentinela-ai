"""Classe base para todos os avaliadores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.esquemas.trace import TraceEntrada as Trace


@dataclass
class ResultadoAvaliador:
    avaliador: str
    score: float  # 0.0 a 1.0
    aprovado: bool
    raciocinio: Optional[str] = None


class AvaliadorBase(ABC):
    """Interface que todo avaliador deve implementar."""

    nome: str
    descricao: str
    threshold: float = 0.7  # score mínimo para "aprovado"

    @abstractmethod
    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        """Avalia um trace e retorna um score entre 0.0 e 1.0."""
        ...

    def _resultado(self, score: float, raciocinio: Optional[str] = None) -> ResultadoAvaliador:
        return ResultadoAvaliador(
            avaliador=self.nome,
            score=round(score, 4),
            aprovado=score >= self.threshold,
            raciocinio=raciocinio,
        )
