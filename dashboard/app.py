"""Entry point do dashboard Sentinela AI."""

import streamlit as st

st.set_page_config(
    page_title="Sentinela AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navegação via sidebar
pagina = st.sidebar.selectbox(
    "Navegação",
    options=["Visão Geral", "Traces"],
    format_func=lambda p: {"Visão Geral": "📊 Visão Geral", "Traces": "🔍 Traces"}[p],
)

if pagina == "Visão Geral":
    from paginas.visao_geral import renderizar
    renderizar()
elif pagina == "Traces":
    from paginas.traces import renderizar
    renderizar()
