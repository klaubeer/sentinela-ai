"""Worker Celery de benchmark — roda avaliadores em um dataset completo."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from app.workers.celery_app import celery_app

logger = logging.getLogger("sentinela.workers.benchmark")

_AVALIADORES_DISPONIVEIS = {
    "faithfulness": "app.avaliadores.faithfulness.AvaliadorFaithfulness",
    "relevancia": "app.avaliadores.relevancia.AvaliadorRelevancia",
    "toxicidade": "app.avaliadores.toxicidade.AvaliadorToxicidade",
    "coerencia": "app.avaliadores.coerencia.AvaliadorCoerencia",
    "deteccao_pii": "app.avaliadores.deteccao_pii.AvaliadorDeteccaoPII",
    "eficiencia_custo": "app.avaliadores.eficiencia_custo.AvaliadorEficienciaCusto",
}


@celery_app.task(name="app.workers.worker_benchmark.rodar_benchmark_task", bind=True, max_retries=2)
def rodar_benchmark_task(
    self,
    dataset_id: str,
    itens: list[dict],
    avaliadores: list[str],
    rotulo: str,
) -> dict:
    """Roda benchmark em todos os itens do dataset e retorna scores agregados."""
    try:
        return asyncio.run(_rodar_benchmark_async(dataset_id, itens, avaliadores, rotulo))
    except Exception as exc:
        logger.error("Falha no benchmark do dataset %s: %s", dataset_id, exc)
        raise self.retry(exc=exc, countdown=5)


async def _rodar_benchmark_async(
    dataset_id: str,
    itens: list[dict],
    nomes_avaliadores: list[str],
    rotulo: str,
) -> dict:
    import importlib

    from app.esquemas.trace import TraceEntrada

    # Instancia os avaliadores solicitados
    avaliadores = []
    for nome in nomes_avaliadores:
        caminho = _AVALIADORES_DISPONIVEIS.get(nome)
        if not caminho:
            logger.warning("Avaliador desconhecido no benchmark: '%s'", nome)
            continue
        modulo_path, classe_nome = caminho.rsplit(".", 1)
        modulo = importlib.import_module(modulo_path)
        avaliadores.append((nome, getattr(modulo, classe_nome)()))

    scores_por_avaliador: dict[str, list[float]] = {nome: [] for nome, _ in avaliadores}

    for item in itens:
        trace = TraceEntrada(
            id=str(uuid.uuid4()),
            projeto=f"benchmark:{dataset_id}",
            nome="benchmark",
            input=item["input"],
            output=item.get("output_esperado"),
            contexto=item.get("contexto"),
        )
        for nome, avaliador in avaliadores:
            try:
                resultado = await avaliador.avaliar(trace)
                scores_por_avaliador[nome].append(resultado.score)
            except Exception as e:
                logger.error("Avaliador %s falhou no item %s: %s", nome, item["id"], e)

    # Agrega resultados
    resumo = {}
    for nome, scores in scores_por_avaliador.items():
        if scores:
            media = sum(scores) / len(scores)
            aprovados = sum(1 for s in scores if s >= 0.7)
            resumo[nome] = {
                "score_medio": round(media, 4),
                "aprovados": aprovados,
                "total": len(scores),
                "taxa_aprovacao": round(aprovados / len(scores), 4),
            }

    logger.info(
        "Benchmark '%s' concluído: %d itens, %d avaliadores",
        rotulo, len(itens), len(avaliadores),
    )

    return {
        "dataset_id": dataset_id,
        "rotulo": rotulo,
        "total_itens": len(itens),
        "resumo": resumo,
    }
