"""CRUD de datasets e endpoint de benchmark."""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.bd.sessao import obter_sessao
from app.modelos.dataset import Dataset, ItemDataset

roteador = APIRouter(prefix="/datasets", tags=["Datasets"])


# ── Schemas de entrada ────────────────────────────────────────────────────────

class ItemEntrada(BaseModel):
    input: Any
    output_esperado: Optional[Any] = None
    contexto: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class DatasetEntrada(BaseModel):
    nome: str
    descricao: Optional[str] = None
    projeto: Optional[str] = None
    itens: list[ItemEntrada] = Field(default_factory=list)


class BenchmarkEntrada(BaseModel):
    avaliadores: list[str] = Field(
        default=["faithfulness", "relevancia"],
        description="Lista de avaliadores a rodar",
    )
    rotulo: Optional[str] = Field(None, description="Ex: 'prompt-v2', 'gpt-4o'")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@roteador.post("", status_code=status.HTTP_201_CREATED)
async def criar_dataset(
    dados: DatasetEntrada,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> dict:
    """Cria um dataset com itens."""
    dataset_id = str(uuid.uuid4())
    dataset = Dataset(
        id=dataset_id,
        nome=dados.nome,
        descricao=dados.descricao,
        projeto=dados.projeto,
    )
    sessao.add(dataset)

    for item in dados.itens:
        sessao.add(ItemDataset(
            id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            input=item.input,
            output_esperado=item.output_esperado,
            contexto=item.contexto,
            metadata_extra=item.metadata,
        ))

    await sessao.commit()
    return {"id": dataset_id, "nome": dados.nome, "total_itens": len(dados.itens)}


@roteador.get("")
async def listar_datasets(
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> list[dict]:
    resultado = await sessao.execute(
        select(Dataset).options(selectinload(Dataset.itens)).order_by(Dataset.criado_em.desc())
    )
    datasets = resultado.scalars().all()
    return [
        {
            "id": d.id,
            "nome": d.nome,
            "descricao": d.descricao,
            "projeto": d.projeto,
            "total_itens": len(d.itens),
            "criado_em": d.criado_em.isoformat(),
        }
        for d in datasets
    ]


@roteador.get("/{dataset_id}")
async def obter_dataset(
    dataset_id: str,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> dict:
    resultado = await sessao.execute(
        select(Dataset).options(selectinload(Dataset.itens)).where(Dataset.id == dataset_id)
    )
    dataset = resultado.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")

    return {
        "id": dataset.id,
        "nome": dataset.nome,
        "descricao": dataset.descricao,
        "projeto": dataset.projeto,
        "criado_em": dataset.criado_em.isoformat(),
        "itens": [
            {
                "id": i.id,
                "input": i.input,
                "output_esperado": i.output_esperado,
                "contexto": i.contexto,
            }
            for i in dataset.itens
        ],
    }


@roteador.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_dataset(
    dataset_id: str,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
) -> None:
    resultado = await sessao.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = resultado.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    await sessao.delete(dataset)
    await sessao.commit()


@roteador.post("/{dataset_id}/benchmark")
async def rodar_benchmark(
    dataset_id: str,
    entrada: BenchmarkEntrada,
    sessao: Annotated[AsyncSession, Depends(obter_sessao)],
    background_tasks: BackgroundTasks,
) -> dict:
    """Roda avaliadores em todos os itens do dataset e retorna scores agregados."""
    resultado_ds = await sessao.execute(
        select(Dataset).options(selectinload(Dataset.itens)).where(Dataset.id == dataset_id)
    )
    dataset = resultado_ds.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")

    if not dataset.itens:
        raise HTTPException(status_code=400, detail="Dataset não tem itens")

    itens = [
        {
            "id": i.id,
            "input": i.input,
            "output_esperado": i.output_esperado,
            "contexto": i.contexto,
        }
        for i in dataset.itens
    ]
    rotulo = entrada.rotulo or dataset.nome

    from app.workers.worker_benchmark import _rodar_benchmark_async
    background_tasks.add_task(
        _rodar_benchmark_async,
        dataset_id=dataset_id,
        itens=itens,
        nomes_avaliadores=entrada.avaliadores,
        rotulo=rotulo,
    )

    return {
        "dataset_id": dataset_id,
        "total_itens": len(dataset.itens),
        "avaliadores": entrada.avaliadores,
        "status": "enfileirado",
    }
