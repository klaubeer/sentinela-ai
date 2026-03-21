"""Entry point da aplicação FastAPI."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alertas, analytics, datasets, drift, ingestao, traces
from app.bd.sessao import Base, engine
from app.configuracao import obter_configuracao

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

config = obter_configuracao()

app = FastAPI(
    title="Sentinela AI",
    description="Plataforma de avaliação e observabilidade para LLMs em produção",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not config.em_producao else ["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestao.roteador)
app.include_router(traces.roteador)
app.include_router(analytics.roteador)
app.include_router(drift.roteador)
app.include_router(datasets.roteador)
app.include_router(alertas.roteador)


@app.on_event("startup")
async def criar_tabelas() -> None:
    """Cria as tabelas no banco na inicialização (usar Alembic em produção)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.getLogger("sentinela").info("Banco de dados inicializado.")


@app.get("/", tags=["Sistema"])
async def raiz() -> dict:
    return {
        "servico": "Sentinela AI",
        "versao": "0.1.0",
        "status": "operacional",
        "docs": "/docs",
    }


@app.get("/saude", tags=["Sistema"])
async def verificar_saude() -> dict:
    return {"status": "saudavel"}
