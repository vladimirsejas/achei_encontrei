import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.auditoria.dominio import TipoEvento
from achei_encontrei.auditoria.modelos import Evento


def registrar_evento(
    sessao: AsyncSession,
    tipo: TipoEvento,
    entidade: str,
    entidade_id: uuid.UUID,
    instituicao_id: uuid.UUID | None = None,
    dados: dict | None = None,
) -> Evento:
    """Adiciona o evento à transação de quem chamou. NÃO faz commit.

    Assim a mudança e o evento que a descreve são gravados juntos, ou nenhum dos dois.
    """
    evento = Evento(
        tipo=tipo,
        entidade=entidade,
        entidade_id=entidade_id,
        instituicao_id=instituicao_id,
        dados=dados or {},
    )
    sessao.add(evento)
    return evento


async def listar_eventos(
    sessao: AsyncSession,
    entidade_id: uuid.UUID | None = None,
    instituicao_id: uuid.UUID | None = None,
    limite: int = 200,
) -> list[Evento]:
    consulta = select(Evento).order_by(Evento.ocorrido_em).limit(limite)
    if entidade_id:
        consulta = consulta.where(Evento.entidade_id == entidade_id)
    if instituicao_id:
        consulta = consulta.where(Evento.instituicao_id == instituicao_id)
    return list((await sessao.scalars(consulta)).all())
