import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from achei_encontrei.auditoria.dominio import TipoEvento
from achei_encontrei.compartilhado.base_modelos import Base, IdMixin, agora_utc


class Evento(IdMixin, Base):
    """Registro imutável de algo que aconteceu. APPEND-ONLY: nunca UPDATE, nunca DELETE."""

    __tablename__ = "eventos"

    tipo: Mapped[TipoEvento] = mapped_column(
        Enum(TipoEvento, native_enum=False, length=40), index=True
    )
    entidade: Mapped[str] = mapped_column(String(40))
    entidade_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    # Permite à instituição ver a trilha de auditoria só dos casos dela.
    instituicao_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, index=True, nullable=True)
    dados: Mapped[dict] = mapped_column(JSON, default=dict)  # nunca guardar dado sensível aqui
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
