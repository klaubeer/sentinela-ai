"""Componentes de gráficos reutilizáveis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def grafico_scores_por_avaliador(traces: list[dict]) -> None:
    """Exibe boxplot de scores agrupados por avaliador."""
    linhas = []
    for trace in traces:
        for av in trace.get("avaliacoes", []):
            linhas.append({"avaliador": av["avaliador"], "score": av["score"]})

    if not linhas:
        st.info("Nenhuma avaliação encontrada ainda.")
        return

    df = pd.DataFrame(linhas)
    fig = px.box(
        df,
        x="avaliador",
        y="score",
        color="avaliador",
        title="Distribuição de Scores por Avaliador",
        range_y=[0, 1],
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)


def grafico_latencia(traces: list[dict]) -> None:
    """Exibe histograma de latência dos traces."""
    latencias = [t["latencia_ms"] for t in traces if t.get("latencia_ms") is not None]
    if not latencias:
        st.info("Sem dados de latência.")
        return

    df = pd.DataFrame({"latencia_ms": latencias})
    fig = px.histogram(
        df,
        x="latencia_ms",
        nbins=30,
        title="Distribuição de Latência (ms)",
        labels={"latencia_ms": "Latência (ms)"},
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def cartao_metrica(label: str, valor: str, delta: str | None = None) -> None:
    st.metric(label=label, value=valor, delta=delta)
