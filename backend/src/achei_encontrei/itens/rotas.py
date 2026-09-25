import uuid
from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.compartilhado.banco import obter_sessao
from achei_encontrei.itens import servicos
from achei_encontrei.itens.esquemas import (
    AchadoComCustodia,
    AchadoOperador,
    AchadoPublico,
    AchadoRegistrarNoBalcao,
    CustodiaLer,
    EntregaAutoridadeCriar,
    ItemPrazo,
    RelatorioInstituicao,
    TransferenciaCriar,
    TransferenciaLer,
)

# Rotas do balcão de uma instituição
rotas_balcao = APIRouter(prefix="/instituicoes/{instituicao_id}", tags=["Balcão"])
# Rotas de um achado específico
rotas_achados = APIRouter(prefix="/achados", tags=["Balcão"])
# Rotina de prazos
rotas_prazos = APIRouter(prefix="/prazos", tags=["Prazo legal"])


def _com_custodia(achado, custodia) -> AchadoComCustodia:
    return AchadoComCustodia(
        **AchadoOperador.model_validate(achado).model_dump(),
        custodia=CustodiaLer.model_validate(custodia),
    )


@rotas_balcao.post(
    "/achados", response_model=AchadoComCustodia, status_code=status.HTTP_201_CREATED
)
async def registrar_no_balcao(
    instituicao_id: uuid.UUID,
    dados: AchadoRegistrarNoBalcao,
    sessao: AsyncSession = Depends(obter_sessao),
):
    achado, custodia = await servicos.registrar_achado_no_balcao(sessao, instituicao_id, dados)
    return _com_custodia(achado, custodia)


@rotas_balcao.get("/achados", response_model=list[AchadoOperador])
async def listar_do_balcao(
    instituicao_id: uuid.UUID,
    apenas_abertos: bool = False,
    sessao: AsyncSession = Depends(obter_sessao),
):
    return await servicos.listar_achados_da_instituicao(sessao, instituicao_id, apenas_abertos)


@rotas_balcao.get("/achados/publicos", response_model=list[AchadoPublico])
async def listar_publicos(instituicao_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)):
    """O que qualquer pessoa pode ver: categoria e data. Nada que permita 'colar' na verificação."""
    abertos = await servicos.listar_achados_da_instituicao(sessao, instituicao_id, True)
    return [
        AchadoPublico(id=a.id, categoria=a.categoria, data_achado=a.data_achado) for a in abertos
    ]


@rotas_balcao.get("/prazos", response_model=list[ItemPrazo])
async def prazos(
    instituicao_id: uuid.UUID,
    hoje: date | None = None,
    sessao: AsyncSession = Depends(obter_sessao),
):
    return await servicos.prazos_da_instituicao(sessao, instituicao_id, hoje or date.today())


@rotas_balcao.get("/relatorio", response_model=RelatorioInstituicao)
async def relatorio(
    instituicao_id: uuid.UUID,
    hoje: date | None = None,
    sessao: AsyncSession = Depends(obter_sessao),
):
    return await servicos.relatorio_instituicao(sessao, instituicao_id, hoje or date.today())


@rotas_achados.get("/{achado_id}", response_model=AchadoComCustodia)
async def obter(achado_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)):
    achado = await servicos.obter_achado(sessao, achado_id)
    custodia = await servicos.obter_custodia(sessao, achado_id)
    return _com_custodia(achado, custodia)


@rotas_achados.get("/{achado_id}/transferencias", response_model=list[TransferenciaLer])
async def listar_transferencias(achado_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)):
    return await servicos.listar_transferencias(sessao, achado_id)


@rotas_achados.post(
    "/{achado_id}/transferencias",
    response_model=TransferenciaLer,
    status_code=status.HTTP_201_CREATED,
)
async def transferir(
    achado_id: uuid.UUID, dados: TransferenciaCriar, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.transferir_custodia(sessao, achado_id, dados)


@rotas_achados.post("/{achado_id}/entrega-autoridade", response_model=AchadoOperador)
async def entrega_autoridade(
    achado_id: uuid.UUID,
    dados: EntregaAutoridadeCriar,
    sessao: AsyncSession = Depends(obter_sessao),
):
    return await servicos.registrar_entrega_autoridade(sessao, achado_id, dados)


@rotas_prazos.post("/verificar")
async def verificar(hoje: date | None = None, sessao: AsyncSession = Depends(obter_sessao)):
    """Rotina diária de alerta. Hoje é acionada manualmente; depois vira agendada."""
    novos = await servicos.verificar_prazos(sessao, hoje or date.today())
    return {"alertas_emitidos": novos}
