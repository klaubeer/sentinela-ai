"""Configuração da aplicação Celery."""

from celery import Celery
from app.configuracao import obter_configuracao

config = obter_configuracao()

celery_app = Celery(
    "sentinela",
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
    include=["app.workers.worker_avaliacao", "app.workers.worker_analytics"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Roda aggregações a cada hora
        "analytics-horario": {
            "task": "app.workers.worker_analytics.calcular_agregacoes",
            "schedule": 3600.0,
        },
    },
)
