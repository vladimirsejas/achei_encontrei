"""Configuração do Alembic (migrações do banco) para SQLAlchemy assíncrono."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

import achei_encontrei.modelos  # noqa: F401 — registra todas as tabelas
from achei_encontrei.compartilhado.base_modelos import Base
from achei_encontrei.compartilhado.config import config as configuracoes

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def rodar_offline() -> None:
    context.configure(
        url=configuracoes.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _executar(conexao) -> None:
    context.configure(connection=conexao, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


async def rodar_online() -> None:
    motor = create_async_engine(configuracoes.database_url)
    async with motor.connect() as conexao:
        await conexao.run_sync(_executar)
    await motor.dispose()


if context.is_offline_mode():
    rodar_offline()
else:
    asyncio.run(rodar_online())
