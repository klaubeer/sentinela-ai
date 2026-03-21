"""Configuração do Alembic para migrations assíncronas."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.bd.sessao import Base
from app.configuracao import obter_configuracao
import app.modelos  # noqa: F401 — garante que os models sejam carregados

config_alembic = context.config
if config_alembic.config_file_name is not None:
    fileConfig(config_alembic.config_file_name)

target_metadata = Base.metadata


def rodar_migrations_offline() -> None:
    url = obter_configuracao().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def rodar_migrations_online() -> None:
    url = obter_configuracao().database_url
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        await conn.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
            )
        )
        await conn.run_sync(lambda _: context.run_migrations())
    await engine.dispose()


if context.is_offline_mode():
    rodar_migrations_offline()
else:
    asyncio.run(rodar_migrations_online())
