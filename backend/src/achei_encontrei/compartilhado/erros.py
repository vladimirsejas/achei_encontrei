"""Erros do domínio. O main.py transforma cada um na resposta HTTP certa, num só lugar."""


class ErroDominio(Exception):
    status_http = 400


class NaoEncontrado(ErroDominio):
    status_http = 404

    def __init__(self, entidade: str, id_):
        super().__init__(f"{entidade} {id_} não encontrado(a).")


class RegraViolada(ErroDominio):
    """Uma regra de negócio impediu a operação (ex.: transição de estado proibida)."""

    status_http = 409


class PermissaoNegada(ErroDominio):
    """Quem pediu não tem direito de fazer isso (ex.: operador de outra instituição)."""

    status_http = 403
