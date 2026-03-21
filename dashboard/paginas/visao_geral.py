"""Página de Visão Geral — KPIs, scores médios e volume de traces."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from componentes.api import buscar_traces, verificar_conexao
from componentes.graficos import grafico_latencia, grafico_scores_por_avaliador


def renderizar() -> None:
    st.title("🛡️ Sentinela AI — Visão Geral")

    # Status da conexão
    if not verificar_conexao():
        st.error("Servidor indisponível. Verifique se o backend está rodando.")
        return

    # Filtros no sidebar
    with st.sidebar:
        st.subheader("Filtros")
        projeto = st.text_input("Projeto", placeholder="ex: vertice-ai")
        limite = st.slider("Traces a carregar", 10, 500, 100)
        apenas_erros = st.checkbox("Apenas com erro")

    dados = buscar_traces(
        projeto=projeto or None,
        com_erro=True if apenas_erros else None,
        limite=limite,
    )
    traces = dados.get("traces", [])

    if not traces:
        st.info("Nenhum trace encontrado. Instrumente seu app com o SDK e envie algumas chamadas.")
        return

    # KPIs
    total = len(traces)
    com_erro = sum(1 for t in traces if t.get("erro"))
    latencias = [t["latencia_ms"] for t in traces if t.get("latencia_ms")]
    latencia_media = sum(latencias) / len(latencias) if latencias else 0

    scores_por_av: dict[str, list[float]] = {}
    for trace in traces:
        for av in trace.get("avaliacoes", []):
            scores_por_av.setdefault(av["avaliador"], []).append(av["score"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Traces", total)
    with col2:
        st.metric("Com Erro", com_erro, delta=f"{com_erro/total*100:.1f}%" if total else "0%")
    with col3:
        st.metric("Latência Média", f"{latencia_media:.0f} ms")
    with col4:
        if scores_por_av:
            avg_geral = sum(
                sum(v) / len(v) for v in scores_por_av.values()
            ) / len(scores_por_av)
            st.metric("Score Médio Geral", f"{avg_geral:.2f}")

    st.divider()

    # Scores médios por avaliador
    if scores_por_av:
        st.subheader("Scores por Avaliador")
        cols = st.columns(len(scores_por_av))
        for col, (avaliador, scores) in zip(cols, scores_por_av.items()):
            media = sum(scores) / len(scores)
            aprovados = sum(1 for s in scores if s >= 0.7)
            with col:
                cor = "normal" if media >= 0.7 else "inverse"
                st.metric(
                    label=avaliador.capitalize(),
                    value=f"{media:.2f}",
                    delta=f"{aprovados}/{len(scores)} aprovados",
                )

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        grafico_scores_por_avaliador(traces)
    with col_b:
        grafico_latencia(traces)

    # Tabela resumo
    st.subheader("Traces Recentes")
    linhas = []
    for t in traces[:20]:
        linhas.append({
            "ID": t["id"][:8] + "...",
            "Projeto": t["projeto"],
            "Função": t["nome"],
            "Latência (ms)": t.get("latencia_ms"),
            "Erro": "✗" if t.get("erro") else "✓",
            "Avaliações": len(t.get("avaliacoes", [])),
            "Criado em": t.get("criado_em", "")[:19],
        })
    st.dataframe(pd.DataFrame(linhas), use_container_width=True)
