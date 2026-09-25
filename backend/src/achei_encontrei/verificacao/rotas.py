import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.compartilhado.banco import obter_sessao
from achei_encontrei.verificacao import servicos
from achei_encontrei.verificacao.esquemas import ContestacaoCriar, DevolucaoCriar, DevolucaoLer

rotas = APIRouter(tags=["Verificação e devolução"])


@rotas.post(
    "/achados/{achado_id}/devolucao",
    response_model=DevolucaoLer,
    status_code=status.HTTP_201_CREATED,
)
async def devolver(
    achado_id: uuid.UUID, dados: DevolucaoCriar, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.registrar_devolucao(sessao, achado_id, dados)


@rotas.get("/achados/{achado_id}/devolucao", response_model=DevolucaoLer)
async def obter(achado_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)):
    return await servicos.obter_devolucao_do_achado(sessao, achado_id)


@rotas.post("/devolucoes/{devolucao_id}/contestacao", response_model=DevolucaoLer)
async def contestar(
    devolucao_id: uuid.UUID, dados: ContestacaoCriar, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.contestar_devolucao(sessao, devolucao_id, dados)
