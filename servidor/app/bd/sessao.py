"""Configuração da sessão assíncrona do banco de dados."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.configuracao import obter_configuracao

config = obter_configuracao()

engine = create_async_engine(
    config.database_url,
    echo=config.ambiente == "desenvolvimento",
    pool_pre_ping=True,
)

FabricaSessao = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe base para todos os models SQLAlchemy."""
    pass


async def obter_sessao() -> AsyncGenerator[AsyncSession, None]:
    """Dependência FastAPI que fornece uma sessão de banco de dados."""
    async with FabricaSessao() as sessao:
        yield sessao
