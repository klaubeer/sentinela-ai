"""Página de Comparações A/B — compara projetos, modelos ou períodos lado a lado."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from componentes.api import buscar_scores_analytics, buscar_traces, verificar_conexao


def renderizar() -> None:
    st.title("⚖️ Comparações A/B")
    st.caption("Compare projetos, versões de prompt ou períodos lado a lado.")

    if not verificar_conexao():
        st.error("Servidor indisponível.")
        return

    with st.sidebar:
        st.subheader("Configuração")
        dias = st.slider("Período (dias)", 1, 30, 7)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Lado A")
        projeto_a = st.text_input("Projeto A", key="proj_a", placeholder="ex: vertice-ai")
    with col_b:
        st.subheader("Lado B")
        projeto_b = st.text_input("Projeto B", key="proj_b", placeholder="ex: postador")

    if not projeto_a or not projeto_b:
        st.info("Preencha os dois projetos para comparar.")
        return

    dados_a = buscar_scores_analytics(projeto=projeto_a, dias=dias)
    dados_b = buscar_scores_analytics(projeto=projeto_b, dias=dias)

    resumo_a = {r["avaliador"]: r for r in dados_a.get("resumo", [])}
    resumo_b = {r["avaliador"]: r for r in dados_b.get("resumo", [])}

    avaliadores = sorted(set(resumo_a.keys()) | set(resumo_b.keys()))

    if not avaliadores:
        st.warning("Nenhuma avaliação encontrada no período para os projetos informados.")
        return

    st.divider()
    st.subheader("Scores por Avaliador")

    # Gráfico de barras agrupadas
    fig = go.Figure()
    scores_a = [resumo_a.get(av, {}).get("score_medio", 0) for av in avaliadores]
    scores_b = [resumo_b.get(av, {}).get("score_medio", 0) for av in avaliadores]

    fig.add_trace(go.Bar(name=projeto_a, x=avaliadores, y=scores_a, marker_color="#2196F3"))
    fig.add_trace(go.Bar(name=projeto_b, x=avaliadores, y=scores_b, marker_color="#FF9800"))
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="Threshold 0.7")
    fig.update_layout(
        barmode="group",
        yaxis_range=[0, 1],
        height=400,
        legend_title="Projeto",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela comparativa
    st.subheader("Tabela Comparativa")
    linhas = []
    for av in avaliadores:
        ra = resumo_a.get(av, {})
        rb = resumo_b.get(av, {})
        score_a = ra.get("score_medio", None)
        score_b = rb.get("score_medio", None)

        if score_a is not None and score_b is not None:
            delta = score_b - score_a
            delta_str = f"{delta:+.4f}"
        else:
            delta_str = "N/A"

        linhas.append({
            "Avaliador": av,
            projeto_a: f"{score_a:.4f}" if score_a is not None else "—",
            projeto_b: f"{score_b:.4f}" if score_b is not None else "—",
            "Diferença (B-A)": delta_str,
        })

    df = pd.DataFrame(linhas)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Métricas de volume
    st.divider()
    st.subheader("Volume e Latência")

    traces_a = buscar_traces(projeto=projeto_a, limite=500)
    traces_b = buscar_traces(projeto=projeto_b, limite=500)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Traces — {projeto_a}", len(traces_a.get("traces", [])))
    with col2:
        st.metric(f"Traces — {projeto_b}", len(traces_b.get("traces", [])))

    lat_a = [t["latencia_ms"] for t in traces_a.get("traces", []) if t.get("latencia_ms")]
    lat_b = [t["latencia_ms"] for t in traces_b.get("traces", []) if t.get("latencia_ms")]

    with col3:
        st.metric(
            f"Latência Média — {projeto_a}",
            f"{sum(lat_a)/len(lat_a):.0f} ms" if lat_a else "—",
        )
    with col4:
        st.metric(
            f"Latência Média — {projeto_b}",
            f"{sum(lat_b)/len(lat_b):.0f} ms" if lat_b else "—",
        )
