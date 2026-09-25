"""Regras puras do ciclo de vida do objeto. Não conhecem banco nem HTTP."""

from datetime import date, timedelta
from enum import StrEnum

from achei_encontrei.compartilhado.config import config
from achei_encontrei.compartilhado.erros import RegraViolada


class Categoria(StrEnum):
    DOCUMENTO = "DOCUMENTO"  # RG, CNH, passaporte, crachá — categoria especial
    ELETRONICO = "ELETRONICO"
    CARTEIRA = "CARTEIRA"
    CHAVE = "CHAVE"
    BOLSA_MOCHILA = "BOLSA_MOCHILA"
    ROUPA_ACESSORIO = "ROUPA_ACESSORIO"
    OUTRO = "OUTRO"


class NivelRisco(StrEnum):
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


# Verificação adaptativa por risco (Atualizações v1, seção 8).
RISCO_POR_CATEGORIA: dict[Categoria, NivelRisco] = {
    Categoria.DOCUMENTO: NivelRisco.ALTO,
    Categoria.ELETRONICO: NivelRisco.MEDIO,
    Categoria.CARTEIRA: NivelRisco.MEDIO,
    Categoria.BOLSA_MOCHILA: NivelRisco.MEDIO,
    Categoria.CHAVE: NivelRisco.BAIXO,
    Categoria.ROUPA_ACESSORIO: NivelRisco.BAIXO,
    Categoria.OUTRO: NivelRisco.BAIXO,
}


def nivel_risco_para(categoria: Categoria) -> NivelRisco:
    return RISCO_POR_CATEGORIA[categoria]


class EstadoAchado(StrEnum):
    REGISTRADO = "REGISTRADO"  # registrado, ainda com quem encontrou (custódia informal)
    EM_MATCH = "EM_MATCH"
    EM_CUSTODIA = "EM_CUSTODIA"  # sob custódia formal de um hub (decisão 0004)
    ENCAMINHADO_AUTORIDADE = "ENCAMINHADO_AUTORIDADE"
    DEVOLVIDO = "DEVOLVIDO"


ESTADOS_ENCERRADOS = {EstadoAchado.DEVOLVIDO, EstadoAchado.ENCAMINHADO_AUTORIDADE}

TRANSICOES_ACHADO: dict[EstadoAchado, set[EstadoAchado]] = {
    EstadoAchado.REGISTRADO: {
        EstadoAchado.EM_MATCH,
        EstadoAchado.EM_CUSTODIA,
        EstadoAchado.DEVOLVIDO,
        EstadoAchado.ENCAMINHADO_AUTORIDADE,
    },
    EstadoAchado.EM_MATCH: {
        EstadoAchado.REGISTRADO,
        EstadoAchado.EM_CUSTODIA,
        EstadoAchado.DEVOLVIDO,
        EstadoAchado.ENCAMINHADO_AUTORIDADE,
    },
    EstadoAchado.EM_CUSTODIA: {
        EstadoAchado.EM_MATCH,
        EstadoAchado.DEVOLVIDO,
        EstadoAchado.ENCAMINHADO_AUTORIDADE,
    },
    EstadoAchado.ENCAMINHADO_AUTORIDADE: set(),
    EstadoAchado.DEVOLVIDO: set(),
}


# Como cada estado é dito para quem está no balcão.
ESTADO_EM_PALAVRAS: dict[EstadoAchado, str] = {
    EstadoAchado.REGISTRADO: "registrado, ainda com quem encontrou",
    EstadoAchado.EM_MATCH: "em análise de correspondência",
    EstadoAchado.EM_CUSTODIA: "guardado no balcão",
    EstadoAchado.ENCAMINHADO_AUTORIDADE: "já entregue à autoridade",
    EstadoAchado.DEVOLVIDO: "já devolvido ao dono",
}


def validar_transicao(atual: EstadoAchado, novo: EstadoAchado) -> None:
    if novo not in TRANSICOES_ACHADO[atual]:
        raise RegraViolada(
            f"Não é possível fazer isso: este objeto está {ESTADO_EM_PALAVRAS[atual]}."
        )


class TipoResponsavel(StrEnum):
    PESSOA = "PESSOA"
    OPERADOR = "OPERADOR"
    INSTITUICAO = "INSTITUICAO"


class DestinoCustodia(StrEnum):
    DEVOLUCAO_DIRETA = "DEVOLUCAO_DIRETA"
    HUB_INSTITUCIONAL = "HUB_INSTITUCIONAL"
    AUTORIDADE_COMPETENTE = "AUTORIDADE_COMPETENTE"


# --- Prazo legal (CP art. 169; CC art. 1.233) ---------------------------------------------------


class SituacaoPrazo(StrEnum):
    NO_PRAZO = "NO_PRAZO"
    PROXIMO_DO_LIMITE = "PROXIMO_DO_LIMITE"
    VENCIDO = "VENCIDO"


def calcular_prazo_legal(data_achado: date) -> date:
    return data_achado + timedelta(days=config.prazo_legal_dias)


def situacao_do_prazo(data_achado: date, hoje: date) -> SituacaoPrazo:
    """O sistema NUNCA encaminha o objeto sozinho à autoridade (decisão 0004).

    O objeto físico continua com alguém. O sistema alerta; o custodiante age e registra.
    """
    if hoje > calcular_prazo_legal(data_achado):
        return SituacaoPrazo.VENCIDO
    if hoje >= data_achado + timedelta(days=config.dias_alerta_prazo):
        return SituacaoPrazo.PROXIMO_DO_LIMITE
    return SituacaoPrazo.NO_PRAZO
