import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.auditoria import servicos
from achei_encontrei.auditoria.esquemas import EventoLer
from achei_encontrei.compartilhado.banco import obter_sessao

rotas = APIRouter(prefix="/eventos", tags=["Auditoria"])


@rotas.get("", response_model=list[EventoLer])
async def listar(
    entidade_id: uuid.UUID | None = None,
    instituicao_id: uuid.UUID | None = None,
    limite: int = Query(200, ge=1, le=1000),
    sessao: AsyncSession = Depends(obter_sessao),
):
    """Trilha de auditoria. Somente leitura: eventos nunca são alterados nem apagados."""
    return await servicos.listar_eventos(sessao, entidade_id, instituicao_id, limite)
