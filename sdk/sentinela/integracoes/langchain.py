"""Integração com LangChain via CallbackHandler."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sentinela.cliente import SentinelaCliente
from sentinela.modelos import Trace

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
except ImportError as e:
    raise ImportError(
        "Para usar a integração com LangChain, instale: pip install sentinela-ai[langchain]"
    ) from e


class SentinelaCallbackHandler(BaseCallbackHandler):
    """Callback do LangChain que captura automaticamente chamadas LLM e envia ao Sentinela.

    Uso:
        from sentinela.integracoes.langchain import SentinelaCallbackHandler

        chain.invoke(input, config={"callbacks": [SentinelaCallbackHandler()]})
    """

    def __init__(
        self,
        cliente: Optional[SentinelaCliente] = None,
        projeto: str = "default",
        nome: str = "langchain",
    ) -> None:
        super().__init__()
        from sentinela.decoradores import _cliente_global

        self._cliente = cliente or _cliente_global
        self._projeto = projeto
        self._nome = nome
        self._inicio: Optional[float] = None
        self._input: Optional[str] = None
        self._modelo: Optional[str] = None

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        self._inicio = time.perf_counter()
        self._input = prompts[0] if prompts else None
        self._modelo = serialized.get("id", [""])[- 1]

    def on_llm_end(self, response: "LLMResult", **kwargs: Any) -> None:
        if self._cliente is None or self._inicio is None:
            return

        latencia_ms = (time.perf_counter() - self._inicio) * 1000
        geracao = response.generations[0][0] if response.generations else None
        output = geracao.text if geracao else None

        uso = response.llm_output or {}
        tokens = uso.get("token_usage", {})

        trace = Trace(
            projeto=self._projeto,
            nome=self._nome,
            input=self._input,
            output=output,
            modelo=self._modelo,
            tokens_entrada=tokens.get("prompt_tokens"),
            tokens_saida=tokens.get("completion_tokens"),
            latencia_ms=round(latencia_ms, 2),
            criado_em=datetime.utcnow(),
        )

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._cliente.enviar_trace(trace))
        except RuntimeError:
            asyncio.run(self._cliente.enviar_trace(trace))
