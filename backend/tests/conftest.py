"""Os testes usam SQLite em memória: rodam em segundos e não precisam do Docker."""

from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import achei_encontrei.modelos  # noqa: F401 — registra todas as tabelas
from achei_encontrei.compartilhado.banco import obter_sessao
from achei_encontrei.compartilhado.base_modelos import Base
from achei_encontrei.main import app


@pytest.fixture
async def cliente():
    motor = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with motor.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    fabrica = async_sessionmaker(motor, expire_on_commit=False)

    async def sessao_de_teste():
        async with fabrica() as s:
            yield s

    app.dependency_overrides[obter_sessao] = sessao_de_teste
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://teste") as c:
        yield c
    app.dependency_overrides.clear()
    await motor.dispose()


@pytest.fixture
async def hub(cliente):
    """Um shopping com uma operadora de balcão."""
    inst = (
        await cliente.post(
            "/instituicoes",
            json={
                "nome": "Shopping Teste",
                "tipo": "SHOPPING",
                "cidade": "Rio Claro",
            },
        )
    ).json()
    op = (
        await cliente.post(
            f"/instituicoes/{inst['id']}/operadores",
            json={
                "nome": "Ana do Balcão",
                "contato": "ana@shopping.com",
            },
        )
    ).json()
    return {"instituicao": inst, "operador": op}


@pytest.fixture
def registrar(cliente, hub):
    """Atalho: registra um achado no balcão do hub, com 'dias_atras' de idade."""

    async def _registrar(categoria="ELETRONICO", dias_atras=0, **extra):
        corpo = {
            "operador_id": hub["operador"]["id"],
            "descricao": "Objeto de teste encontrado no local",
            "sinais_privados": "Adesivo de banda na parte de trás",
            "categoria": categoria,
            "local_encontrado": "Praça de alimentação",
            "data_achado": str(date.today() - timedelta(days=dias_atras)),
            "local_guarda": "Armário 3 do balcão",
            **extra,
        }
        r = await cliente.post(f"/instituicoes/{hub['instituicao']['id']}/achados", json=corpo)
        assert r.status_code == 201, r.text
        return r.json()

    return _registrar


async def tipos_de_evento(cliente, entidade_id):
    r = await cliente.get("/eventos", params={"entidade_id": entidade_id})
    return [e["tipo"] for e in r.json()]
