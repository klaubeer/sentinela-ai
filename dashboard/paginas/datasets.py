"""Página de Datasets — visualiza e gerencia datasets de regressão."""

from __future__ import annotations

import streamlit as st

from componentes.api import verificar_conexao

import httpx
import os

SERVIDOR_URL = os.getenv("SERVIDOR_URL", "http://localhost:8000")


def _listar_datasets() -> list[dict]:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.get("/datasets")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Erro ao buscar datasets: {e}")
        return []


def _rodar_benchmark(dataset_id: str, avaliadores: list[str]) -> dict | None:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=15) as c:
            r = c.post(
                f"/datasets/{dataset_id}/benchmark",
                json={"avaliadores": avaliadores},
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Erro ao iniciar benchmark: {e}")
        return None


def _deletar_dataset(dataset_id: str) -> bool:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as c:
            r = c.delete(f"/datasets/{dataset_id}")
            return r.status_code == 204
    except Exception:
        return False


def renderizar() -> None:
    st.title("📋 Datasets")
    st.caption("Gerencie datasets de regressão e rode benchmarks.")

    if not verificar_conexao():
        st.error("Servidor indisponível.")
        return

    datasets = _listar_datasets()

    if not datasets:
        st.info("Nenhum dataset encontrado. Crie um via API ou script de seed.")
        _mostrar_exemplo_curl()
        return

    for ds in datasets:
        with st.expander(f"📂 {ds['nome']}  —  {ds['total_itens']} itens"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**ID:** `{ds['id']}`")
                if ds.get("projeto"):
                    st.markdown(f"**Projeto:** `{ds['projeto']}`")
                if ds.get("descricao"):
                    st.caption(ds["descricao"])
                st.caption(f"Criado em: {ds['criado_em'][:10]}")

            with col2:
                avaliadores_sel = st.multiselect(
                    "Avaliadores",
                    options=["faithfulness", "relevancia", "toxicidade", "coerencia", "deteccao_pii"],
                    default=["faithfulness", "relevancia"],
                    key=f"av_{ds['id']}",
                )
                if st.button("▶ Rodar Benchmark", key=f"bench_{ds['id']}"):
                    resultado = _rodar_benchmark(ds["id"], avaliadores_sel)
                    if resultado:
                        st.success(f"Benchmark enfileirado! Task ID: `{resultado['task_id']}`")

                if st.button("🗑 Deletar", key=f"del_{ds['id']}", type="secondary"):
                    if _deletar_dataset(ds["id"]):
                        st.success("Dataset deletado.")
                        st.rerun()


def _mostrar_exemplo_curl() -> None:
    with st.expander("Como criar um dataset via API"):
        st.code("""
curl -X POST http://localhost:8000/datasets \\
  -H "Content-Type: application/json" \\
  -d '{
    "nome": "golden-v1",
    "projeto": "meu-projeto",
    "itens": [
      {
        "input": "Qual o prazo de entrega?",
        "output_esperado": "O prazo é 5 dias úteis.",
        "contexto": "Prazo padrão: 5 dias úteis para capitais."
      }
    ]
  }'
        """, language="bash")
