import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.compartilhado.banco import obter_sessao
from achei_encontrei.identidade import servicos
from achei_encontrei.identidade.esquemas import (
    InstituicaoCriar,
    InstituicaoLer,
    OperadorCriar,
    OperadorLer,
)

rotas = APIRouter(prefix="/instituicoes", tags=["Identidade"])


@rotas.post("", response_model=InstituicaoLer, status_code=status.HTTP_201_CREATED)
async def criar_instituicao(dados: InstituicaoCriar, sessao: AsyncSession = Depends(obter_sessao)):
    return await servicos.criar_instituicao(sessao, dados)


@rotas.get("", response_model=list[InstituicaoLer])
async def listar_instituicoes(sessao: AsyncSession = Depends(obter_sessao)):
    return await servicos.listar_instituicoes(sessao)


@rotas.get("/{instituicao_id}", response_model=InstituicaoLer)
async def obter_instituicao(
    instituicao_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.obter_instituicao(sessao, instituicao_id)


@rotas.post(
    "/{instituicao_id}/operadores",
    response_model=OperadorLer,
    status_code=status.HTTP_201_CREATED,
)
async def criar_operador(
    instituicao_id: uuid.UUID, dados: OperadorCriar, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.criar_operador(sessao, instituicao_id, dados)


@rotas.get("/{instituicao_id}/operadores", response_model=list[OperadorLer])
async def listar_operadores(
    instituicao_id: uuid.UUID, sessao: AsyncSession = Depends(obter_sessao)
):
    return await servicos.listar_operadores(sessao, instituicao_id)
