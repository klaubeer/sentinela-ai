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
    "Visão Geral":  "📊 Visão Geral",
    "Traces":       "🔍 Traces",
    "Avaliações":   "📈 Avaliações",
    "Comparações":  "⚖️ Comparações A/B",
    "Datasets":     "📋 Datasets",
    "Alertas":      "🔔 Alertas",
}

pagina = st.sidebar.selectbox(
    "Navegação",
    options=list(_PAGINAS.keys()),
    format_func=lambda p: _PAGINAS[p],
)

if pagina == "Visão Geral":
    from paginas.visao_geral import renderizar
elif pagina == "Traces":
    from paginas.traces import renderizar
elif pagina == "Avaliações":
    from paginas.avaliacoes import renderizar
elif pagina == "Comparações":
    from paginas.comparacoes import renderizar
elif pagina == "Datasets":
    from paginas.datasets import renderizar
elif pagina == "Alertas":
    from paginas.alertas import renderizar

renderizar()
