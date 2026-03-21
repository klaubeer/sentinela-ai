"""Entry point do dashboard Sentinela AI."""

import streamlit as st

st.set_page_config(
    page_title="Sentinela AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navegação via sidebar
_PAGINAS = {
    "Visão Geral": "📊 Visão Geral",
    "Traces": "🔍 Traces",
    "Avaliações": "📈 Avaliações",
}

pagina = st.sidebar.selectbox(
    "Navegação",
    options=list(_PAGINAS.keys()),
    format_func=lambda p: _PAGINAS[p],
)

if pagina == "Visão Geral":
    from paginas.visao_geral import renderizar
    renderizar()
elif pagina == "Traces":
    from paginas.traces import renderizar
    renderizar()
elif pagina == "Avaliações":
    from paginas.avaliacoes import renderizar
    renderizar()
