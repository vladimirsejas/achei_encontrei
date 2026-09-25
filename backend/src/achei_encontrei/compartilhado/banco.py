"""Conexão assíncrona com o banco e a sessão entregue a cada requisição."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from achei_encontrei.compartilhado.config import config

motor = create_async_engine(config.database_url)
FabricaSessao = async_sessionmaker(motor, expire_on_commit=False)


async def obter_sessao() -> AsyncIterator[AsyncSession]:
    async with FabricaSessao() as sessao:
        yield sessao
