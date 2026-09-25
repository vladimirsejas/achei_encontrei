"""Verificação adaptativa por risco (Atualizações v1, seção 8).

Quanto maior o risco do objeto, mais forte a verificação exigida.
"""

from enum import StrEnum

from achei_encontrei.compartilhado.erros import RegraViolada
from achei_encontrei.itens.dominio import NivelRisco


class TipoDocumento(StrEnum):
    """Qual documento o operador conferiu. O NÚMERO do documento nunca é guardado (LGPD)."""

    RG = "RG"
    CNH = "CNH"
    PASSAPORTE = "PASSAPORTE"
    OUTRO = "OUTRO"
    NENHUM = "NENHUM"


class StatusContestacao(StrEnum):
    NAO_CONTESTADA = "NAO_CONTESTADA"
    CONTESTADA = "CONTESTADA"


MINIMO_RESUMO_POR_RISCO = {
    NivelRisco.BAIXO: 5,
    NivelRisco.MEDIO: 20,
    NivelRisco.ALTO: 20,
}


def validar_verificacao(
    nivel_risco: NivelRisco, tipo_documento: TipoDocumento, resumo: str
) -> None:
    """Confere se a verificação feita pelo operador é proporcional ao risco do objeto.

    - BAIXO (chave, roupa): uma descrição curta do que a pessoa informou basta.
    - MÉDIO (celular, carteira): descrição detalhada dos sinais conferidos.
    - ALTO (documentos): descrição detalhada E um documento de identificação conferido.

    Quem decide é sempre o operador, um humano. O sistema só impede verificação fraca demais.
    """
    minimo = MINIMO_RESUMO_POR_RISCO[nivel_risco]
    if len(resumo.strip()) < minimo:
        raise RegraViolada(
            f"Para objetos de risco {nivel_risco}, descreva com pelo menos {minimo} caracteres "
            "o que a pessoa informou e o que foi conferido."
        )
    if nivel_risco == NivelRisco.ALTO and tipo_documento == TipoDocumento.NENHUM:
        raise RegraViolada(
            "Objetos de risco ALTO só podem ser devolvidos após conferência de um documento "
            "de identificação do reivindicante."
        )
