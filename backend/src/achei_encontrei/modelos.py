"""Importa todos os modelos: é o que o Alembic e os testes usam para enxergar todas as tabelas."""

from achei_encontrei.auditoria.modelos import Evento
from achei_encontrei.identidade.modelos import Instituicao, Operador, Pessoa
from achei_encontrei.itens.modelos import Achado, Custodia, TransferenciaCustodia
from achei_encontrei.verificacao.modelos import Devolucao

__all__ = [
    "Evento",
    "Pessoa",
    "Instituicao",
    "Operador",
    "Achado",
    "Custodia",
    "TransferenciaCustodia",
    "Devolucao",
]
