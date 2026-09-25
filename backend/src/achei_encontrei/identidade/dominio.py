from enum import StrEnum


class TipoInstituicao(StrEnum):
    SHOPPING = "SHOPPING"
    RODOVIARIA = "RODOVIARIA"
    AEROPORTO = "AEROPORTO"
    HOTEL = "HOTEL"
    HOSPITAL = "HOSPITAL"
    UNIVERSIDADE = "UNIVERSIDADE"
    EVENTO = "EVENTO"
    OUTRO = "OUTRO"


class NivelAcesso(StrEnum):
    BASICO = "BASICO"  # registra achados, movimenta custódia, conduz devoluções
    SUPERVISOR = "SUPERVISOR"  # além disso: gerencia operadores e vê relatórios completos
