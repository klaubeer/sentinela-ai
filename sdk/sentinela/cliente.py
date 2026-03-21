"""Cliente HTTP async para envio de traces ao servidor Sentinela."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from .modelos import Trace

logger = logging.getLogger("sentinela.cliente")


class SentinelaCliente:
    """Cliente HTTP async que envia traces ao servidor em background (fire-and-forget)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 5.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
            timeout=timeout,
        )

    async def enviar_trace(self, trace: Trace) -> bool:
        """Envia um trace para o servidor. Retorna True se bem-sucedido.

        Falhas são logadas mas não propagadas — o sistema monitorado não pode
        ser afetado por problemas no Sentinela.
        """
        try:
            resposta = await self._http.post(
                "/traces",
                content=trace.model_dump_json(),
            )
            resposta.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Sentinela: falha ao enviar trace %s — HTTP %d: %s",
                trace.id,
                e.response.status_code,
                e.response.text,
            )
        except Exception as e:
            logger.warning("Sentinela: falha ao enviar trace %s — %s", trace.id, e)
        return False

    async def fechar(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "SentinelaCliente":
        return self

    async def __aexit__(self, *_) -> None:
        await self.fechar()
