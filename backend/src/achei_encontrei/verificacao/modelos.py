import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from achei_encontrei.compartilhado.base_modelos import Base, IdMixin, agora_utc
from achei_encontrei.verificacao.dominio import StatusContestacao, TipoDocumento


class Devolucao(IdMixin, Base):
    """ERD v0.1 — Devolução."""

    __tablename__ = "devolucoes"

    achado_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("achados.id"), unique=True)
    custodia_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("custodias.id"))
    # Nulo quando a pessoa foi direto ao balcão, sem passar pelo matching (decisão 0004).
    # Vira chave estrangeira quando a tabela de Match existir (Fase 3).
    match_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    operador_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operadores.id"))
    reivindicante_nome: Mapped[str] = mapped_column(String(120))
    reivindicante_contato: Mapped[str] = mapped_column(String(160))  # classe Interno
    tipo_documento_conferido: Mapped[TipoDocumento] = mapped_column(
        Enum(TipoDocumento, native_enum=False, length=20)
    )
    verificacao_resumo: Mapped[str] = mapped_column(Text)
    achadego_registrado: Mapped[bool] = mapped_column(Boolean, default=False)
    status_contestacao: Mapped[StatusContestacao] = mapped_column(
        Enum(StatusContestacao, native_enum=False, length=20),
        default=StatusContestacao.NAO_CONTESTADA,
    )
    realizada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
