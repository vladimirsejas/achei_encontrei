from datetime import date

import pytest

from achei_encontrei.compartilhado.erros import RegraViolada
from achei_encontrei.itens.dominio import (
    TRANSICOES_ACHADO,
    Categoria,
    EstadoAchado,
    NivelRisco,
    SituacaoPrazo,
    calcular_prazo_legal,
    nivel_risco_para,
    situacao_do_prazo,
    validar_transicao,
)


def test_toda_categoria_tem_risco():
    for c in Categoria:
        nivel_risco_para(c)
    assert nivel_risco_para(Categoria.DOCUMENTO) == NivelRisco.ALTO


def test_prazo_legal_de_15_dias():
    assert calcular_prazo_legal(date(2026, 9, 25)) == date(2026, 10, 10)


@pytest.mark.parametrize(
    "hoje, esperado",
    [
        (date(2026, 9, 5), SituacaoPrazo.NO_PRAZO),  # dia 4
        (date(2026, 9, 11), SituacaoPrazo.PROXIMO_DO_LIMITE),  # dia 10
        (date(2026, 9, 16), SituacaoPrazo.PROXIMO_DO_LIMITE),  # dia 15: último dia
        (date(2026, 9, 17), SituacaoPrazo.VENCIDO),  # dia 16
    ],
)
def test_situacao_do_prazo(hoje, esperado):
    assert situacao_do_prazo(date(2026, 9, 1), hoje) == esperado


def test_estados_encerrados_sao_finais():
    for estado in (EstadoAchado.DEVOLVIDO, EstadoAchado.ENCAMINHADO_AUTORIDADE):
        assert TRANSICOES_ACHADO[estado] == set()
    with pytest.raises(RegraViolada):
        validar_transicao(EstadoAchado.DEVOLVIDO, EstadoAchado.EM_CUSTODIA)


def test_tabela_cobre_todos_os_estados():
    assert set(TRANSICOES_ACHADO) == set(EstadoAchado)
