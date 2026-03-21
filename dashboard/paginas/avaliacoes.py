"""Página de Avaliações — trends de scores ao longo do tempo por avaliador."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from componentes.api import buscar_projetos_analytics, buscar_scores_analytics, verificar_conexao

# Cores consistentes por avaliador
_CORES_AVALIADOR = {
    "faithfulness": "#2196F3",
    "relevancia": "#4CAF50",
    "toxicidade": "#F44336",
    "coerencia": "#FF9800",
    "deteccao_pii": "#9C27B0",
    "eficiencia_custo": "#00BCD4",
}


def renderizar() -> None:
    st.title("📈 Avaliações — Trends e Scores")

    if not verificar_conexao():
        st.error("Servidor indisponível.")
        return

    with st.sidebar:
        st.subheader("Filtros")
        projetos_dados = buscar_projetos_analytics(dias=30)
        nomes_projetos = ["Todos"] + [p["projeto"] for p in projetos_dados.get("projetos", [])]
        projeto_sel = st.selectbox("Projeto", nomes_projetos)
        dias = st.slider("Período (dias)", 1, 30, 7)

    projeto = None if projeto_sel == "Todos" else projeto_sel
    dados = buscar_scores_analytics(projeto=projeto, dias=dias)

    resumo = dados.get("resumo", [])
    serie = dados.get("serie_temporal", [])

    if not resumo:
        st.info("Nenhuma avaliação no período selecionado.")
        return

    # Cards de score médio por avaliador
    st.subheader("Score Médio por Avaliador")
    cols = st.columns(min(len(resumo), 4))
    for col, r in zip(cols, resumo):
        cor = "normal" if r["score_medio"] >= 0.7 else "inverse"
        with col:
            st.metric(
                label=r["avaliador"].replace("_", " ").capitalize(),
                value=f"{r['score_medio']:.2f}",
                delta=f"{r['taxa_aprovacao']*100:.0f}% aprovados",
            )

    st.divider()

    if serie:
        df_serie = pd.DataFrame(serie)
        df_serie["dia"] = pd.to_datetime(df_serie["dia"])

        # Gráfico de linha: score médio ao longo do tempo
        st.subheader("Evolução dos Scores")
        fig = px.line(
            df_serie,
            x="dia",
            y="score_medio",
            color="avaliador",
            markers=True,
            range_y=[0, 1],
            labels={"dia": "Data", "score_medio": "Score Médio", "avaliador": "Avaliador"},
            color_discrete_map=_CORES_AVALIADOR,
        )
        fig.add_hline(
            y=0.7,
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold mínimo (0.7)",
            annotation_position="bottom right",
        )
        fig.update_layout(height=400, legend_title="Avaliador")
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap: score por avaliador × dia
        st.subheader("Heatmap de Scores")
        df_pivot = df_serie.pivot_table(
            index="avaliador",
            columns=df_serie["dia"].dt.strftime("%d/%m"),
            values="score_medio",
            aggfunc="mean",
        )
        fig_heat = px.imshow(
            df_pivot,
            color_continuous_scale="RdYlGn",
            zmin=0,
            zmax=1,
            aspect="auto",
            labels={"x": "Data", "y": "Avaliador", "color": "Score"},
        )
        fig_heat.update_layout(height=300)
        st.plotly_chart(fig_heat, use_container_width=True)

    # Tabela detalhada
    st.subheader("Resumo Detalhado")
    df_resumo = pd.DataFrame(resumo)
    df_resumo.columns = ["Avaliador", "Score Médio", "Total", "Aprovados", "Taxa de Aprovação"]
    df_resumo["Taxa de Aprovação"] = df_resumo["Taxa de Aprovação"].apply(lambda x: f"{x*100:.1f}%")
    df_resumo["Score Médio"] = df_resumo["Score Médio"].apply(lambda x: f"{x:.4f}")
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)
