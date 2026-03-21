"""Worker Celery de avaliação — processa traces em background."""

from __future__ import annotations

import asyncio
import logging
import uuid

from app.workers.celery_app import celery_app

logger = logging.getLogger("sentinela.workers.avaliacao")


@celery_app.task(name="app.workers.worker_avaliacao.avaliar_trace", bind=True, max_retries=3)
def avaliar_trace(self, trace_dados: dict) -> dict:
    """Tarefa Celery que roda avaliadores e guardrails para um trace."""
    try:
        return asyncio.run(_avaliar_trace_async(trace_dados))
    except Exception as exc:
        logger.error("Falha ao avaliar trace %s: %s", trace_dados.get("id"), exc)
        raise self.retry(exc=exc, countdown=2**self.request.retries)


async def _avaliar_trace_async(trace_dados: dict) -> dict:
    from app.avaliadores.base import AvaliadorBase
    from app.avaliadores.coerencia import AvaliadorCoerencia
    from app.avaliadores.deteccao_pii import AvaliadorDeteccaoPII
    from app.avaliadores.eficiencia_custo import AvaliadorEficienciaCusto
    from app.avaliadores.faithfulness import AvaliadorFaithfulness
    from app.avaliadores.relevancia import AvaliadorRelevancia
    from app.avaliadores.toxicidade import AvaliadorToxicidade
    from app.bd.sessao import FabricaSessao
    from app.esquemas.trace import TraceEntrada
    from app.modelos.trace import ResultadoAvaliacao
    from app.nucleo.guardrails import MotorGuardrails

    trace = TraceEntrada(**trace_dados)

    avaliadores: list[AvaliadorBase] = [
        AvaliadorFaithfulness(),
        AvaliadorRelevancia(),
        AvaliadorToxicidade(),
        AvaliadorCoerencia(),
        AvaliadorDeteccaoPII(),
        AvaliadorEficienciaCusto(),
    ]

    resultados = []
    violacoes_guardrail: list[str] = []

    async with FabricaSessao() as sessao:
        # Roda avaliadores
        for avaliador in avaliadores:
            try:
                resultado = await avaliador.avaliar(trace)
                orm = ResultadoAvaliacao(
                    id=str(uuid.uuid4()),
                    trace_id=trace.id,
                    avaliador=resultado.avaliador,
                    score=resultado.score,
                    aprovado=resultado.aprovado,
                    raciocinio=resultado.raciocinio,
                )
                sessao.add(orm)
                resultados.append({
                    "avaliador": resultado.avaliador,
                    "score": resultado.score,
                    "aprovado": resultado.aprovado,
                })
                logger.info(
                    "Trace %s — %s: %.2f (%s)",
                    trace.id,
                    resultado.avaliador,
                    resultado.score,
                    "✓" if resultado.aprovado else "✗",
                )
            except Exception as e:
                logger.error("Avaliador %s falhou para trace %s: %s", avaliador.nome, trace.id, e)

        # Roda guardrails se configurados nos metadados do trace
        guardrails_config = trace.metadata.get("guardrails", [])
        if guardrails_config:
            motor = MotorGuardrails(guardrails=guardrails_config)
            resultado_guardrail = await motor.verificar(trace)
            violacoes_guardrail = resultado_guardrail.violacoes

            if not resultado_guardrail.passou:
                # Persiste cada violação como um resultado de avaliação especial
                for violacao in resultado_guardrail.violacoes:
                    orm_guardrail = ResultadoAvaliacao(
                        id=str(uuid.uuid4()),
                        trace_id=trace.id,
                        avaliador=f"guardrail:{violacao}",
                        score=0.0,
                        aprovado=False,
                        raciocinio=resultado_guardrail.detalhes.get(violacao),
                    )
                    sessao.add(orm_guardrail)

        await sessao.commit()

    return {
        "trace_id": trace.id,
        "resultados": resultados,
        "violacoes_guardrail": violacoes_guardrail,
    }
