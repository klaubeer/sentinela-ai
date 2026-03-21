"""Decorator @observe() — instrumenta funções para enviar traces ao Sentinela."""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from datetime import datetime
from typing import Any, Callable, Optional

from .cliente import SentinelaCliente
from .modelos import Trace

logger = logging.getLogger("sentinela.decoradores")

# Cliente global configurado via Sentinela.inicializar()
_cliente_global: Optional[SentinelaCliente] = None
_projeto_global: str = "default"


def _obter_cliente() -> Optional[SentinelaCliente]:
    return _cliente_global


def _serializar_args(args: tuple, kwargs: dict) -> Any:
    """Tenta converter args/kwargs em algo serializável."""
    if args and not kwargs:
        return args[0] if len(args) == 1 else list(args)
    if kwargs and not args:
        return kwargs
    return {"args": list(args), "kwargs": kwargs}


def observe(
    nome: Optional[str] = None,
    projeto: Optional[str] = None,
    capturar_input: bool = True,
    capturar_output: bool = True,
):
    """Decorator que instrumenta uma função e envia o trace ao Sentinela.

    Uso:
        @observe()
        def meu_chatbot(pergunta: str) -> str:
            ...

        @observe(nome="atendimento", projeto="vertice-ai")
        async def atender(pergunta: str) -> str:
            ...
    """

    def decorador(func: Callable) -> Callable:
        trace_nome = nome or func.__name__
        trace_projeto = projeto or _projeto_global

        @functools.wraps(func)
        async def _executar_async(*args, **kwargs) -> Any:
            cliente = _obter_cliente()
            inicio = datetime.utcnow()
            inicio_ts = time.perf_counter()
            output = None
            erro = None

            try:
                output = await func(*args, **kwargs)
                return output
            except Exception as exc:
                erro = f"{type(exc).__name__}: {exc}"
                raise
            finally:
                latencia_ms = (time.perf_counter() - inicio_ts) * 1000
                if cliente is not None:
                    trace = Trace(
                        projeto=trace_projeto,
                        nome=trace_nome,
                        input=_serializar_args(args, kwargs) if capturar_input else None,
                        output=output if capturar_output else None,
                        latencia_ms=round(latencia_ms, 2),
                        criado_em=inicio,
                        erro=erro,
                    )
                    # Fire-and-forget: não bloqueia nem propaga falhas
                    asyncio.create_task(cliente.enviar_trace(trace))

        @functools.wraps(func)
        def _executar_sync(*args, **kwargs) -> Any:
            cliente = _obter_cliente()
            inicio = datetime.utcnow()
            inicio_ts = time.perf_counter()
            output = None
            erro = None

            try:
                output = func(*args, **kwargs)
                return output
            except Exception as exc:
                erro = f"{type(exc).__name__}: {exc}"
                raise
            finally:
                latencia_ms = (time.perf_counter() - inicio_ts) * 1000
                if cliente is not None:
                    trace = Trace(
                        projeto=trace_projeto,
                        nome=trace_nome,
                        input=_serializar_args(args, kwargs) if capturar_input else None,
                        output=output if capturar_output else None,
                        latencia_ms=round(latencia_ms, 2),
                        criado_em=inicio,
                        erro=erro,
                    )
                    # Para funções sync, tenta usar o event loop ativo ou cria um novo
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(cliente.enviar_trace(trace))
                    except RuntimeError:
                        asyncio.run(cliente.enviar_trace(trace))

        if asyncio.iscoroutinefunction(func):
            return _executar_async
        return _executar_sync

    return decorador
