"""Avaliador de Eficiência de Custo — relação custo/qualidade do trace."""

from __future__ import annotations

import logging

from app.esquemas.trace import TraceEntrada as Trace

from .base import AvaliadorBase, ResultadoAvaliador

logger = logging.getLogger("sentinela.avaliadores.eficiencia_custo")

# Custo por 1M de tokens (USD) — referência para cálculo de custo estimado
_CUSTO_POR_MILHAO: dict[str, dict[str, float]] = {
    "gpt-4o": {"entrada": 2.50, "saida": 10.00},
    "gpt-4o-mini": {"entrada": 0.15, "saida": 0.60},
    "gpt-4-turbo": {"entrada": 10.00, "saida": 30.00},
    "gpt-3.5-turbo": {"entrada": 0.50, "saida": 1.50},
    "claude-3-5-sonnet": {"entrada": 3.00, "saida": 15.00},
    "claude-3-haiku": {"entrada": 0.25, "saida": 1.25},
}
_CUSTO_PADRAO = {"entrada": 1.00, "saida": 3.00}

# Limites de custo por trace para benchmarking
_CUSTO_OTIMO_USD = 0.001   # abaixo de $0.001 = eficiente
_CUSTO_ACEITAVEL_USD = 0.01  # abaixo de $0.01 = aceitável
_CUSTO_ALTO_USD = 0.05     # acima de $0.05 = caro


class AvaliadorEficienciaCusto(AvaliadorBase):
    nome = "eficiencia_custo"
    descricao = "Avalia a relação custo/qualidade baseada em tokens e modelo utilizado"
    threshold = 0.5

    async def avaliar(self, trace: Trace) -> ResultadoAvaliador:
        custo = trace.custo_usd

        # Calcula custo estimado se não veio do SDK
        if custo is None and trace.modelo and (trace.tokens_entrada or trace.tokens_saida):
            custo = _estimar_custo(
                modelo=trace.modelo,
                tokens_entrada=trace.tokens_entrada or 0,
                tokens_saida=trace.tokens_saida or 0,
            )

        if custo is None:
            return self._resultado(
                score=1.0,
                raciocinio="Dados de custo insuficientes para avaliação",
            )

        if custo <= _CUSTO_OTIMO_USD:
            score = 1.0
            descricao = f"Custo ótimo: ${custo:.6f}"
        elif custo <= _CUSTO_ACEITAVEL_USD:
            # Escala linear entre ótimo e aceitável
            fator = (custo - _CUSTO_OTIMO_USD) / (_CUSTO_ACEITAVEL_USD - _CUSTO_OTIMO_USD)
            score = 1.0 - (fator * 0.3)
            descricao = f"Custo aceitável: ${custo:.6f}"
        elif custo <= _CUSTO_ALTO_USD:
            fator = (custo - _CUSTO_ACEITAVEL_USD) / (_CUSTO_ALTO_USD - _CUSTO_ACEITAVEL_USD)
            score = 0.7 - (fator * 0.4)
            descricao = f"Custo elevado: ${custo:.6f}"
        else:
            score = 0.1
            descricao = f"Custo muito alto: ${custo:.6f}"

        return self._resultado(score=max(0.0, round(score, 4)), raciocinio=descricao)


def _estimar_custo(modelo: str, tokens_entrada: int, tokens_saida: int) -> float:
    chave = next((k for k in _CUSTO_POR_MILHAO if k in modelo.lower()), None)
    precos = _CUSTO_POR_MILHAO.get(chave, _CUSTO_PADRAO) if chave else _CUSTO_PADRAO
    return (tokens_entrada * precos["entrada"] + tokens_saida * precos["saida"]) / 1_000_000
