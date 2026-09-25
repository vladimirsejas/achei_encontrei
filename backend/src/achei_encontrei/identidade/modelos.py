import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from achei_encontrei.compartilhado.base_modelos import Base, CriadoEmMixin, IdMixin
from achei_encontrei.identidade.dominio import NivelAcesso, TipoInstituicao


class Pessoa(IdMixin, CriadoEmMixin, Base):
    """ERD v0.1 — Pessoa. Contato é dado interno: nunca aparece em resposta pública."""

    __tablename__ = "pessoas"

    nome: Mapped[str] = mapped_column(String(120))
    contato: Mapped[str] = mapped_column(String(160))


class Instituicao(IdMixin, CriadoEmMixin, Base):
    """ERD v0.1 — Instituição (o hub: shopping, rodoviária, hotel...)."""

    __tablename__ = "instituicoes"

    nome: Mapped[str] = mapped_column(String(160))
    tipo: Mapped[TipoInstituicao] = mapped_column(
        Enum(TipoInstituicao, native_enum=False, length=20)
    )
    cidade: Mapped[str] = mapped_column(String(120))
    hub_custodia: Mapped[bool] = mapped_column(Boolean, default=True)


class Operador(IdMixin, CriadoEmMixin, Base):
    """ERD v0.1 — Operador: uma Pessoa que age em nome de uma Instituição."""

    __tablename__ = "operadores"

    pessoa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pessoas.id"), index=True)
    instituicao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("instituicoes.id"), index=True)
    nivel_acesso: Mapped[NivelAcesso] = mapped_column(
        Enum(NivelAcesso, native_enum=False, length=20), default=NivelAcesso.BASICO
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
