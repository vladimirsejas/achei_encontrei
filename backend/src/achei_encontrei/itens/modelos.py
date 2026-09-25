import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from achei_encontrei.compartilhado.base_modelos import Base, CriadoEmMixin, IdMixin, agora_utc
from achei_encontrei.itens.dominio import (
    Categoria,
    DestinoCustodia,
    EstadoAchado,
    NivelRisco,
    TipoResponsavel,
)


class Achado(IdMixin, CriadoEmMixin, Base):
    """ERD v0.1 — Achado."""

    __tablename__ = "achados"

    # Hub onde o objeto está (nulo quando o achado é registrado por um cidadão — Fase 2).
    instituicao_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("instituicoes.id"), index=True, nullable=True
    )
    registrado_por_operador_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("operadores.id"), nullable=True
    )
    descricao: Mapped[str] = mapped_column(Text)  # classe Interno
    # Sinais que só o verdadeiro dono saberia (ex.: "adesivo de banda atrás").
    # Classe Sensível: nunca aparece em listagem pública. Base da verificação cega.
    sinais_privados: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[Categoria] = mapped_column(Enum(Categoria, native_enum=False, length=30))
    nivel_risco: Mapped[NivelRisco] = mapped_column(Enum(NivelRisco, native_enum=False, length=10))
    local_encontrado: Mapped[str] = mapped_column(String(200))
    data_achado: Mapped[date] = mapped_column(Date)
    prazo_legal_entrega: Mapped[date] = mapped_column(Date, index=True)
    achadego_informado: Mapped[bool] = mapped_column(Boolean, default=False)
    alerta_prazo_emitido: Mapped[bool] = mapped_column(Boolean, default=False)
    estado: Mapped[EstadoAchado] = mapped_column(
        Enum(EstadoAchado, native_enum=False, length=30), index=True
    )


class Custodia(IdMixin, Base):
    """ERD v0.1 — Custódia. Todo achado tem exatamente uma (relação 1..1)."""

    __tablename__ = "custodias"

    achado_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("achados.id"), unique=True)
    # Responsável polimórfico: tipo + id (decisão 0004).
    responsavel_tipo: Mapped[TipoResponsavel] = mapped_column(
        Enum(TipoResponsavel, native_enum=False, length=20)
    )
    responsavel_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    local_fisico: Mapped[str] = mapped_column(String(200))
    iniciada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    encerrada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    destino: Mapped[DestinoCustodia | None] = mapped_column(
        Enum(DestinoCustodia, native_enum=False, length=30), nullable=True
    )


class TransferenciaCustodia(IdMixin, Base):
    """ERD v0.1 — cada mudança de responsável, para sempre registrada."""

    __tablename__ = "transferencias_custodia"

    custodia_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("custodias.id"), index=True)
    de_tipo: Mapped[TipoResponsavel] = mapped_column(
        Enum(TipoResponsavel, native_enum=False, length=20)
    )
    de_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    para_tipo: Mapped[TipoResponsavel] = mapped_column(
        Enum(TipoResponsavel, native_enum=False, length=20)
    )
    para_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    local_fisico: Mapped[str] = mapped_column(String(200))
    motivo: Mapped[str] = mapped_column(String(300))
    operador_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("operadores.id"), nullable=True
    )
    ocorrida_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
