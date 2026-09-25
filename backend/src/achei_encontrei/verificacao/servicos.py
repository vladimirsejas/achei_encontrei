import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.auditoria.dominio import TipoEvento
from achei_encontrei.auditoria.servicos import registrar_evento
from achei_encontrei.compartilhado.erros import NaoEncontrado, RegraViolada
from achei_encontrei.identidade.servicos import exigir_operador_da_instituicao
from achei_encontrei.itens import servicos as itens
from achei_encontrei.itens.dominio import DestinoCustodia, EstadoAchado
from achei_encontrei.verificacao.dominio import StatusContestacao, validar_verificacao
from achei_encontrei.verificacao.esquemas import ContestacaoCriar, DevolucaoCriar
from achei_encontrei.verificacao.modelos import Devolucao


async def registrar_devolucao(
    sessao: AsyncSession, achado_id: uuid.UUID, dados: DevolucaoCriar
) -> Devolucao:
    """A pessoa foi ao balcão, o operador verificou a reivindicação e entregou o objeto."""
    achado = await itens.obter_achado(sessao, achado_id)
    await exigir_operador_da_instituicao(sessao, dados.operador_id, achado.instituicao_id)
    validar_verificacao(
        achado.nivel_risco, dados.tipo_documento_conferido, dados.verificacao_resumo
    )

    itens.mudar_estado(achado, EstadoAchado.DEVOLVIDO)
    custodia = await itens.encerrar_custodia(sessao, achado, DestinoCustodia.DEVOLUCAO_DIRETA)

    devolucao = Devolucao(
        achado_id=achado.id,
        custodia_id=custodia.id,
        operador_id=dados.operador_id,
        reivindicante_nome=dados.reivindicante_nome,
        reivindicante_contato=dados.reivindicante_contato,
        tipo_documento_conferido=dados.tipo_documento_conferido,
        verificacao_resumo=dados.verificacao_resumo,
        achadego_registrado=dados.achadego_registrado,
    )
    sessao.add(devolucao)
    await sessao.flush()

    registrar_evento(
        sessao,
        TipoEvento.VERIFICACAO_APROVADA,
        "Achado",
        achado.id,
        achado.instituicao_id,
        {
            "nivel_risco": achado.nivel_risco,
            "documento": dados.tipo_documento_conferido,
            "operador_id": str(dados.operador_id),
        },
    )
    registrar_evento(
        sessao,
        TipoEvento.DEVOLUCAO_REALIZADA,
        "Devolucao",
        devolucao.id,
        achado.instituicao_id,
        {"achado_id": str(achado.id), "achadego_registrado": dados.achadego_registrado},
    )
    await sessao.commit()
    return devolucao


async def obter_devolucao_do_achado(sessao: AsyncSession, achado_id: uuid.UUID) -> Devolucao:
    devolucao = await sessao.scalar(select(Devolucao).where(Devolucao.achado_id == achado_id))
    if devolucao is None:
        raise NaoEncontrado("Devolução do achado", achado_id)
    return devolucao


async def contestar_devolucao(
    sessao: AsyncSession, devolucao_id: uuid.UUID, dados: ContestacaoCriar
) -> Devolucao:
    """Reabre o caso para revisão humana SEM apagar o registro original (auditabilidade)."""
    devolucao = await sessao.get(Devolucao, devolucao_id)
    if devolucao is None:
        raise NaoEncontrado("Devolução", devolucao_id)
    if devolucao.status_contestacao == StatusContestacao.CONTESTADA:
        raise RegraViolada("Esta devolução já está contestada e em revisão.")
    achado = await itens.obter_achado(sessao, devolucao.achado_id)
    devolucao.status_contestacao = StatusContestacao.CONTESTADA
    registrar_evento(
        sessao,
        TipoEvento.REIVINDICACAO_CONTESTADA,
        "Devolucao",
        devolucao.id,
        achado.instituicao_id,
        {"motivo": dados.motivo},
    )
    await sessao.commit()
    return devolucao
