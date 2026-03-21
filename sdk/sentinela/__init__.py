"""Sentinela AI — SDK de observabilidade e avaliação para LLMs em produção."""

from __future__ import annotations

from typing import Optional

from .cliente import SentinelaCliente
from .decoradores import observe
from .decoradores import _cliente_global as _estado_cliente
from .modelos import ResultadoAvaliacao, Span, Trace

import sentinela.decoradores as _decoradores


class Sentinela:
    """Ponto de entrada principal do SDK.

    Uso:
        sentinela = Sentinela(api_key="sk-...", projeto="meu-projeto")

        @sentinela.observe()
        def minha_funcao(pergunta):
            ...
    """

    def __init__(
        self,
        api_key: str,
        projeto: str = "default",
        base_url: str = "http://localhost:8000",
    ) -> None:
        self.api_key = api_key
        self.projeto = projeto
        self.base_url = base_url

        cliente = SentinelaCliente(api_key=api_key, base_url=base_url)
        _decoradores._cliente_global = cliente
        _decoradores._projeto_global = projeto

    def observe(
        self,
        nome: Optional[str] = None,
        capturar_input: bool = True,
        capturar_output: bool = True,
    ):
        """Decorator que instrumenta uma função. Equivalente ao @observe() global."""
        return observe(
            nome=nome,
            projeto=self.projeto,
            capturar_input=capturar_input,
            capturar_output=capturar_output,
        )


__all__ = [
    "Sentinela",
    "observe",
    "Trace",
    "Span",
    "ResultadoAvaliacao",
    "SentinelaCliente",
]
