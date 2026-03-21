"""Página de Alertas — configura regras e visualiza histórico de disparos."""

from __future__ import annotations

import os

import httpx
import pandas as pd
import streamlit as st

from componentes.api import verificar_conexao

SERVIDOR_URL = os.getenv("SERVIDOR_URL", "http://localhost:8000")

_AVALIADORES = [
    "faithfulness", "relevancia", "toxicidade",
    "coerencia", "deteccao_pii", "eficiencia_custo",
]


def _listar_regras(projeto: str | None = None) -> list[dict]:
    try:
        params = {"projeto": projeto} if projeto else {}
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.get("/alertas/regras", params=params)
            r.raise_for_status()
            return r.json()
    except Exception:
        return []


def _historico(projeto: str | None = None) -> list[dict]:
    try:
        params = {"projeto": projeto} if projeto else {}
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.get("/alertas/historico", params=params)
            r.raise_for_status()
            return r.json()
    except Exception:
        return []


def _criar_regra(dados: dict) -> bool:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.post("/alertas/regras", json=dados)
            r.raise_for_status()
            return True
    except Exception as e:
        st.error(f"Erro ao criar regra: {e}")
        return False


def _deletar_regra(regra_id: str) -> bool:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.delete(f"/alertas/regras/{regra_id}")
            return r.status_code == 204
    except Exception:
        return False


def renderizar() -> None:
    st.title("🔔 Alertas")

    if not verificar_conexao():
        st.error("Servidor indisponível.")
        return

    with st.sidebar:
        st.subheader("Filtros")
        projeto_filtro = st.text_input("Filtrar por projeto", placeholder="ex: vertice-ai")

    aba_regras, aba_historico, aba_nova = st.tabs(["Regras Ativas", "Histórico", "Nova Regra"])

    # ── Regras ativas ───────────────────────────────────────────────────────
    with aba_regras:
        regras = _listar_regras(projeto_filtro or None)
        if not regras:
            st.info("Nenhuma regra configurada.")
        else:
            for r in regras:
                with st.expander(
                    f"{'🟢' if r['ativa'] else '⚫'} {r['nome']}  "
                    f"— {r['avaliador']} < {r['threshold']} por {r['janela_minutos']}min"
                ):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(
                            f"**Projeto:** `{r['projeto']}` &nbsp;|&nbsp; "
                            f"**Canal:** {r['canal'].upper()} &nbsp;|&nbsp; "
                            f"Criado em: {r['criado_em'][:10]}"
                        )
                    with col2:
                        if st.button("🗑 Remover", key=f"del_{r['id']}"):
                            if _deletar_regra(r["id"]):
                                st.success("Regra removida.")
                                st.rerun()

    # ── Histórico ───────────────────────────────────────────────────────────
    with aba_historico:
        historico = _historico(projeto_filtro or None)
        if not historico:
            st.info("Nenhum alerta disparado ainda.")
        else:
            df = pd.DataFrame([
                {
                    "Disparado em": a["disparado_em"][:19],
                    "Projeto": a["projeto"],
                    "Avaliador": a["avaliador"],
                    "Score": f"{a['score_medio']:.2f}",
                    "Threshold": f"{a['threshold']:.2f}",
                    "Mensagem": a["mensagem"],
                }
                for a in historico
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Nova regra ──────────────────────────────────────────────────────────
    with aba_nova:
        st.subheader("Criar nova regra de alerta")
        with st.form("nova_regra"):
            nome = st.text_input("Nome da regra", placeholder="ex: Faithfulness crítico")
            projeto = st.text_input("Projeto", placeholder="ex: vertice-ai")
            avaliador = st.selectbox("Avaliador monitorado", _AVALIADORES)
            threshold = st.slider("Threshold mínimo", 0.0, 1.0, 0.7, 0.05)
            janela = st.slider("Janela de tempo (minutos)", 5, 1440, 60, 5)
            canal = st.radio("Canal", ["slack", "discord"], horizontal=True)
            webhook = st.text_input("Webhook URL", placeholder="https://hooks.slack.com/...")

            if st.form_submit_button("Criar Regra", type="primary"):
                if not all([nome, projeto, webhook]):
                    st.error("Preencha todos os campos obrigatórios.")
                elif _criar_regra({
                    "nome": nome,
                    "projeto": projeto,
                    "avaliador": avaliador,
                    "threshold": threshold,
                    "janela_minutos": janela,
                    "canal": canal,
                    "webhook_url": webhook,
                }):
                    st.success(f"Regra '{nome}' criada com sucesso!")
                    st.rerun()
