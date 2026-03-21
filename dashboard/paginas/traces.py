"""Página de exploração de traces individuais."""

from __future__ import annotations

import json

import streamlit as st

from componentes.api import buscar_trace, buscar_traces, verificar_conexao


def renderizar() -> None:
    st.title("🔍 Explorador de Traces")

    if not verificar_conexao():
        st.error("Servidor indisponível.")
        return

    # Filtros no sidebar
    with st.sidebar:
        st.subheader("Filtros")
        projeto = st.text_input("Projeto", placeholder="ex: vertice-ai")
        nome_funcao = st.text_input("Função", placeholder="ex: atender_cliente")
        apenas_erros = st.checkbox("Apenas com erro")
        limite = st.slider("Traces a carregar", 10, 200, 50)

    dados = buscar_traces(
        projeto=projeto or None,
        nome=nome_funcao or None,
        com_erro=True if apenas_erros else None,
        limite=limite,
    )
    traces = dados.get("traces", [])

    if not traces:
        st.info("Nenhum trace encontrado com os filtros atuais.")
        return

    # Lista de traces como tabela selecionável
    st.subheader(f"{len(traces)} traces encontrados")

    opcoes = {
        f"{t['id'][:8]}... | {t['projeto']} | {t['nome']} | {t.get('criado_em', '')[:19]}": t["id"]
        for t in traces
    }

    selecionado_label = st.selectbox("Selecione um trace para inspecionar:", list(opcoes.keys()))
    trace_id = opcoes[selecionado_label]

    trace = buscar_trace(trace_id)
    if trace is None:
        return

    _renderizar_trace(trace)


def _renderizar_trace(trace: dict) -> None:
    st.divider()

    # Cabeçalho
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Projeto:** `{trace['projeto']}`")
        st.markdown(f"**Função:** `{trace['nome']}`")
    with col2:
        st.markdown(f"**Modelo:** `{trace.get('modelo') or 'N/A'}`")
        st.markdown(f"**Latência:** `{trace.get('latencia_ms', 'N/A')} ms`")
    with col3:
        tokens_e = trace.get("tokens_entrada") or 0
        tokens_s = trace.get("tokens_saida") or 0
        st.markdown(f"**Tokens:** `{tokens_e} entrada / {tokens_s} saída`")
        st.markdown(f"**Custo:** `${trace.get('custo_usd') or 0:.6f}`")

    if trace.get("erro"):
        st.error(f"Erro: {trace['erro']}")

    st.divider()

    # Input / Output / Contexto
    col_input, col_output = st.columns(2)
    with col_input:
        st.subheader("Input")
        _exibir_valor(trace.get("input"))

    with col_output:
        st.subheader("Output")
        _exibir_valor(trace.get("output"))

    if trace.get("contexto"):
        with st.expander("Contexto RAG"):
            st.text(trace["contexto"])

    # Avaliações
    avaliacoes = trace.get("avaliacoes", [])
    if avaliacoes:
        st.subheader("Avaliações")
        cols = st.columns(len(avaliacoes))
        for col, av in zip(cols, avaliacoes):
            with col:
                cor = "🟢" if av["aprovado"] else "🔴"
                st.metric(
                    label=f"{cor} {av['avaliador'].capitalize()}",
                    value=f"{av['score']:.2f}",
                )
                if av.get("raciocinio"):
                    st.caption(av["raciocinio"])
    else:
        st.info("Nenhuma avaliação disponível para este trace.")


def _exibir_valor(valor) -> None:
    if valor is None:
        st.text("N/A")
    elif isinstance(valor, (dict, list)):
        st.json(valor)
    else:
        st.text_area("", value=str(valor), height=150, label_visibility="collapsed")
