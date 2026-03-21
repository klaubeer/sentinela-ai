"""Notificador — envia alertas via webhook para Slack ou Discord."""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

logger = logging.getLogger("sentinela.nucleo.notificador")


async def notificar_slack(webhook_url: str, mensagem: dict) -> bool:
    """Envia mensagem formatada para o Slack via webhook."""
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "⚠️ Sentinela AI — Alerta de Qualidade"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Projeto:*\n{mensagem['projeto']}"},
                    {"type": "mrkdwn", "text": f"*Avaliador:*\n{mensagem['avaliador']}"},
                    {"type": "mrkdwn", "text": f"*Score atual:*\n`{mensagem['score_medio']:.2f}`"},
                    {"type": "mrkdwn", "text": f"*Threshold:*\n`{mensagem['threshold']:.2f}`"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"_{mensagem['detalhe']}_"},
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Disparado em {mensagem['disparado_em']}"},
                ],
            },
        ]
    }
    return await _enviar_webhook(webhook_url, payload)


async def notificar_discord(webhook_url: str, mensagem: dict) -> bool:
    """Envia embed formatado para o Discord via webhook."""
    payload = {
        "embeds": [
            {
                "title": "⚠️ Sentinela AI — Alerta de Qualidade",
                "color": 0xFF4444,  # vermelho
                "fields": [
                    {"name": "Projeto", "value": mensagem["projeto"], "inline": True},
                    {"name": "Avaliador", "value": mensagem["avaliador"], "inline": True},
                    {"name": "Score atual", "value": f"`{mensagem['score_medio']:.2f}`", "inline": True},
                    {"name": "Threshold", "value": f"`{mensagem['threshold']:.2f}`", "inline": True},
                    {"name": "Detalhe", "value": mensagem["detalhe"], "inline": False},
                ],
                "footer": {"text": f"Disparado em {mensagem['disparado_em']}"},
            }
        ]
    }
    return await _enviar_webhook(webhook_url, payload)


async def _enviar_webhook(url: str, payload: dict) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resposta = await client.post(url, json=payload)
            resposta.raise_for_status()
            return True
    except Exception as e:
        logger.error("Falha ao enviar webhook para %s: %s", url, e)
        return False
