"""Casos de uso do balcão.

Convenção: funções que representam uma operação completa fazem commit no final.
Funções marcadas com "NÃO faz commit" são peças usadas por outros módulos dentro
da transação deles.
"""

import uuid
from collections import Counter
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.auditoria.dominio import TipoEvento
from achei_encontrei.auditoria.servicos import registrar_evento
from achei_encontrei.compartilhado.base_modelos import agora_utc
from achei_encontrei.compartilhado.erros import NaoEncontrado, RegraViolada
from achei_encontrei.identidade.servicos import exigir_operador_da_instituicao, obter_instituicao
from achei_encontrei.itens.dominio import (
    ESTADOS_ENCERRADOS,
    DestinoCustodia,
    EstadoAchado,
    SituacaoPrazo,
    TipoResponsavel,
    calcular_prazo_legal,
    nivel_risco_para,
    situacao_do_prazo,
    validar_transicao,
)
from achei_encontrei.itens.esquemas import (
    AchadoRegistrarNoBalcao,
    EntregaAutoridadeCriar,
    ItemPrazo,
    RelatorioInstituicao,
    TransferenciaCriar,
)
from achei_encontrei.itens.modelos import Achado, Custodia, TransferenciaCustodia

# --- Registro no balcão -------------------------------------------------------------------------


async def registrar_achado_no_balcao(
    sessao: AsyncSession, instituicao_id: uuid.UUID, dados: AchadoRegistrarNoBalcao
) -> tuple[Achado, Custodia]:
    """O objeto chega ao balcão: nasce o achado, e junto com ele a custódia do hub."""
    await obter_instituicao(sessao, instituicao_id)
    await exigir_operador_da_instituicao(sessao, dados.operador_id, instituicao_id)

    achado = Achado(
        instituicao_id=instituicao_id,
        registrado_por_operador_id=dados.operador_id,
        descricao=dados.descricao,
        sinais_privados=dados.sinais_privados,
        categoria=dados.categoria,
        nivel_risco=nivel_risco_para(dados.categoria),
        local_encontrado=dados.local_encontrado,
        data_achado=dados.data_achado,
        prazo_legal_entrega=calcular_prazo_legal(dados.data_achado),
        achadego_informado=dados.achadego_informado,
        estado=EstadoAchado.EM_CUSTODIA,
    )
    sessao.add(achado)
    await sessao.flush()

    custodia = Custodia(
        achado_id=achado.id,
        responsavel_tipo=TipoResponsavel.INSTITUICAO,
        responsavel_id=instituicao_id,
        local_fisico=dados.local_guarda,
    )
    sessao.add(custodia)
    await sessao.flush()

    registrar_evento(
        sessao,
        TipoEvento.ACHADO_CRIADO,
        "Achado",
        achado.id,
        instituicao_id,
        {
            "categoria": achado.categoria,
            "prazo_legal_entrega": achado.prazo_legal_entrega.isoformat(),
            "operador_id": str(dados.operador_id),
        },
    )
    registrar_evento(
        sessao,
        TipoEvento.CUSTODIA_INICIADA,
        "Custodia",
        custodia.id,
        instituicao_id,
        {"achado_id": str(achado.id), "local_fisico": custodia.local_fisico},
    )
    if achado.achadego_informado:
        registrar_evento(sessao, TipoEvento.ACHADEGO_INFORMADO, "Achado", achado.id, instituicao_id)

    await sessao.commit()
    return achado, custodia


# --- Consultas ----------------------------------------------------------------------------------


async def obter_achado(sessao: AsyncSession, achado_id: uuid.UUID) -> Achado:
    achado = await sessao.get(Achado, achado_id)
    if achado is None:
        raise NaoEncontrado("Achado", achado_id)
    return achado


async def obter_custodia(sessao: AsyncSession, achado_id: uuid.UUID) -> Custodia:
    custodia = await sessao.scalar(select(Custodia).where(Custodia.achado_id == achado_id))
    if custodia is None:
        raise NaoEncontrado("Custódia do achado", achado_id)
    return custodia


async def listar_transferencias(
    sessao: AsyncSession, achado_id: uuid.UUID
) -> list[TransferenciaCustodia]:
    custodia = await obter_custodia(sessao, achado_id)
    consulta = (
        select(TransferenciaCustodia)
        .where(TransferenciaCustodia.custodia_id == custodia.id)
        .order_by(TransferenciaCustodia.ocorrida_em)
    )
    return list((await sessao.scalars(consulta)).all())


async def listar_achados_da_instituicao(
    sessao: AsyncSession, instituicao_id: uuid.UUID, apenas_abertos: bool = False
) -> list[Achado]:
    await obter_instituicao(sessao, instituicao_id)
    consulta = select(Achado).where(Achado.instituicao_id == instituicao_id)
    if apenas_abertos:
        consulta = consulta.where(Achado.estado.not_in(ESTADOS_ENCERRADOS))
    consulta = consulta.order_by(Achado.data_achado.desc())
    return list((await sessao.scalars(consulta)).all())


# --- Peças usadas por outros módulos (NÃO fazem commit) -----------------------------------------


def mudar_estado(achado: Achado, novo: EstadoAchado) -> EstadoAchado:
    """Valida e aplica a transição. NÃO faz commit. Devolve o estado anterior."""
    anterior = achado.estado
    validar_transicao(anterior, novo)
    achado.estado = novo
    return anterior


async def encerrar_custodia(
    sessao: AsyncSession, achado: Achado, destino: DestinoCustodia
) -> Custodia:
    """Fecha a cadeia de custódia com o destino final. NÃO faz commit."""
    custodia = await obter_custodia(sessao, achado.id)
    if custodia.encerrada_em is not None:
        raise RegraViolada("A custódia deste achado já foi encerrada.")
    custodia.encerrada_em = agora_utc()
    custodia.destino = destino
    return custodia


# --- Movimentação de custódia ------------------------------------------------------------------


async def transferir_custodia(
    sessao: AsyncSession, achado_id: uuid.UUID, dados: TransferenciaCriar
) -> TransferenciaCustodia:
    achado = await obter_achado(sessao, achado_id)
    await exigir_operador_da_instituicao(sessao, dados.operador_id, achado.instituicao_id)
    custodia = await obter_custodia(sessao, achado_id)
    if custodia.encerrada_em is not None:
        raise RegraViolada("Não é possível transferir: a custódia já foi encerrada.")

    transferencia = TransferenciaCustodia(
        custodia_id=custodia.id,
        de_tipo=custodia.responsavel_tipo,
        de_id=custodia.responsavel_id,
        para_tipo=dados.para_tipo,
        para_id=dados.para_id,
        local_fisico=dados.local_fisico,
        motivo=dados.motivo,
        operador_id=dados.operador_id,
    )
    sessao.add(transferencia)
    custodia.responsavel_tipo = dados.para_tipo
    custodia.responsavel_id = dados.para_id
    custodia.local_fisico = dados.local_fisico
    await sessao.flush()

    registrar_evento(
        sessao,
        TipoEvento.CUSTODIA_TRANSFERIDA,
        "Custodia",
        custodia.id,
        achado.instituicao_id,
        {"achado_id": str(achado.id), "para_tipo": dados.para_tipo, "motivo": dados.motivo},
    )
    await sessao.commit()
    return transferencia


async def registrar_entrega_autoridade(
    sessao: AsyncSession, achado_id: uuid.UUID, dados: EntregaAutoridadeCriar
) -> Achado:
    """O custodiante levou o objeto à autoridade competente (CC art. 1.233, par. único)."""
    achado = await obter_achado(sessao, achado_id)
    await exigir_operador_da_instituicao(sessao, dados.operador_id, achado.instituicao_id)
    mudar_estado(achado, EstadoAchado.ENCAMINHADO_AUTORIDADE)
    await encerrar_custodia(sessao, achado, DestinoCustodia.AUTORIDADE_COMPETENTE)
    registrar_evento(
        sessao,
        TipoEvento.ENTREGA_AUTORIDADE_REGISTRADA,
        "Achado",
        achado.id,
        achado.instituicao_id,
        {"orgao": dados.orgao, "protocolo": dados.protocolo, "operador_id": str(dados.operador_id)},
    )
    await sessao.commit()
    return achado


# --- Prazo legal -------------------------------------------------------------------------------


async def prazos_da_instituicao(
    sessao: AsyncSession, instituicao_id: uuid.UUID, hoje: date
) -> list[ItemPrazo]:
    """Achados ainda abertos, do mais urgente para o menos urgente."""
    abertos = await listar_achados_da_instituicao(sessao, instituicao_id, apenas_abertos=True)
    itens = [
        ItemPrazo(
            achado_id=a.id,
            categoria=a.categoria,
            data_achado=a.data_achado,
            prazo_legal_entrega=a.prazo_legal_entrega,
            situacao=situacao_do_prazo(a.data_achado, hoje),
            dias_restantes=(a.prazo_legal_entrega - hoje).days,
        )
        for a in abertos
    ]
    return sorted(itens, key=lambda i: i.dias_restantes)


async def verificar_prazos(sessao: AsyncSession, hoje: date) -> int:
    """Rotina diária: emite PRAZO_ENTREGA_PROXIMO_DO_LIMITE uma única vez por achado.

    Devolve quantos alertas novos foram emitidos. No futuro roda sozinha todo dia;
    por enquanto é chamada pela rota /prazos/verificar.
    """
    consulta = select(Achado).where(
        Achado.estado.not_in(ESTADOS_ENCERRADOS),
        Achado.alerta_prazo_emitido.is_(False),
    )
    novos = 0
    for achado in (await sessao.scalars(consulta)).all():
        situacao = situacao_do_prazo(achado.data_achado, hoje)
        if situacao in (SituacaoPrazo.PROXIMO_DO_LIMITE, SituacaoPrazo.VENCIDO):
            achado.alerta_prazo_emitido = True
            registrar_evento(
                sessao,
                TipoEvento.PRAZO_ENTREGA_PROXIMO_DO_LIMITE,
                "Achado",
                achado.id,
                achado.instituicao_id,
                {
                    "prazo_legal_entrega": achado.prazo_legal_entrega.isoformat(),
                    "situacao": situacao,
                },
            )
            novos += 1
    await sessao.commit()
    return novos


# --- Relatório para a instituição --------------------------------------------------------------


async def relatorio_instituicao(
    sessao: AsyncSession, instituicao_id: uuid.UUID, hoje: date
) -> RelatorioInstituicao:
    """O que o gestor e o jurídico da instituição querem ver (ver O-02 em oportunidades.md)."""
    achados = await listar_achados_da_instituicao(sessao, instituicao_id)
    estados = Counter(a.estado for a in achados)
    devolvidos = estados[EstadoAchado.DEVOLVIDO]
    encaminhados = estados[EstadoAchado.ENCAMINHADO_AUTORIDADE]
    encerrados = devolvidos + encaminhados

    abertos = [a for a in achados if a.estado not in ESTADOS_ENCERRADOS]
    situacoes = Counter(situacao_do_prazo(a.data_achado, hoje) for a in abertos)

    return RelatorioInstituicao(
        instituicao_id=instituicao_id,
        gerado_em=hoje,
        total_registrados=len(achados),
        em_custodia=len(abertos),
        devolvidos=devolvidos,
        encaminhados_autoridade=encaminhados,
        # A métrica central do projeto: do que foi encerrado, quanto voltou ao dono?
        taxa_devolucao_percentual=round(100 * devolvidos / encerrados, 1) if encerrados else None,
        prazos_proximos_do_limite=situacoes[SituacaoPrazo.PROXIMO_DO_LIMITE],
        prazos_vencidos_sem_destino=situacoes[SituacaoPrazo.VENCIDO],
        por_categoria=dict(Counter(str(a.categoria) for a in achados)),
    )
