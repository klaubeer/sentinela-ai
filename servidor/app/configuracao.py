"""Configurações da aplicação via variáveis de ambiente."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Banco de dados
    database_url: str = "postgresql+asyncpg://sentinela:sentinela@localhost:5432/sentinela"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_secret_key: str = "desenvolvimento-sem-seguranca"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ambiente: str = "desenvolvimento"

    # LLM para avaliadores
    openai_api_key: str = ""
    modelo_avaliacao: str = "gpt-4o-mini"

    @property
    def em_producao(self) -> bool:
        return self.ambiente == "producao"


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()
