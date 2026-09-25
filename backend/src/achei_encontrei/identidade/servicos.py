import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from achei_encontrei.compartilhado.erros import NaoEncontrado, PermissaoNegada
from achei_encontrei.identidade.esquemas import InstituicaoCriar, OperadorCriar, OperadorLer
from achei_encontrei.identidade.modelos import Instituicao, Operador, Pessoa


async def criar_instituicao(sessao: AsyncSession, dados: InstituicaoCriar) -> Instituicao:
    instituicao = Instituicao(**dados.model_dump())
    sessao.add(instituicao)
    await sessao.commit()
    return instituicao


async def obter_instituicao(sessao: AsyncSession, instituicao_id: uuid.UUID) -> Instituicao:
    instituicao = await sessao.get(Instituicao, instituicao_id)
    if instituicao is None:
        raise NaoEncontrado("Instituição", instituicao_id)
    return instituicao


async def criar_operador(
    sessao: AsyncSession, instituicao_id: uuid.UUID, dados: OperadorCriar
) -> OperadorLer:
    await obter_instituicao(sessao, instituicao_id)
    pessoa = Pessoa(nome=dados.nome, contato=dados.contato)
    sessao.add(pessoa)
    await sessao.flush()
    operador = Operador(
        pessoa_id=pessoa.id, instituicao_id=instituicao_id, nivel_acesso=dados.nivel_acesso
    )
    sessao.add(operador)
    await sessao.commit()
    return _para_leitura(operador, pessoa)


async def listar_operadores(sessao: AsyncSession, instituicao_id: uuid.UUID) -> list[OperadorLer]:
    await obter_instituicao(sessao, instituicao_id)
    consulta = (
        select(Operador, Pessoa)
        .join(Pessoa, Pessoa.id == Operador.pessoa_id)
        .where(Operador.instituicao_id == instituicao_id)
    )
    return [_para_leitura(o, p) for o, p in (await sessao.execute(consulta)).all()]


async def exigir_operador_da_instituicao(
    sessao: AsyncSession, operador_id: uuid.UUID, instituicao_id: uuid.UUID
) -> Operador:
    """Garante que o operador existe, está ativo e trabalha nesta instituição.

    É a regra de permissão central do balcão: um operador do Shopping A
    nunca mexe nos objetos do Hotel B.
    """
    operador = await sessao.get(Operador, operador_id)
    if operador is None:
        raise NaoEncontrado("Operador", operador_id)
    if not operador.ativo or operador.instituicao_id != instituicao_id:
        raise PermissaoNegada("Este operador não pode agir em nome desta instituição.")
    return operador


def _para_leitura(operador: Operador, pessoa: Pessoa) -> OperadorLer:
    return OperadorLer(
        id=operador.id,
        instituicao_id=operador.instituicao_id,
        nome=pessoa.nome,
        nivel_acesso=operador.nivel_acesso,
        ativo=operador.ativo,
    )
