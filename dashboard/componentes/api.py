"""Cliente HTTP para comunicação com o servidor Sentinela."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
import streamlit as st

SERVIDOR_URL = os.getenv("SERVIDOR_URL", "http://localhost:8000")


@st.cache_data(ttl=30)
def buscar_traces(
    projeto: Optional[str] = None,
    nome: Optional[str] = None,
    com_erro: Optional[bool] = None,
    limite: int = 100,
    pagina: int = 1,
) -> dict:
    params: dict[str, Any] = {"limite": limite, "pagina": pagina}
    if projeto:
        params["projeto"] = projeto
    if nome:
        params["nome"] = nome
    if com_erro is not None:
        params["com_erro"] = com_erro

    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as client:
            r = client.get("/traces", params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Erro ao buscar traces: {e}")
        return {"traces": [], "total": 0, "pagina": 1, "limite": limite}


@st.cache_data(ttl=30)
def buscar_trace(trace_id: str) -> Optional[dict]:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=10) as client:
            r = client.get(f"/traces/{trace_id}")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Erro ao buscar trace {trace_id}: {e}")
        return None


def verificar_conexao() -> bool:
    try:
        with httpx.Client(base_url=SERVIDOR_URL, timeout=3) as client:
            r = client.get("/saude")
            return r.status_code == 200
    except Exception:
        return False
