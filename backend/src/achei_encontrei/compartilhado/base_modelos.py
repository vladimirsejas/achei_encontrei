"""Base declarativa do SQLAlchemy e colunas comuns a todas as tabelas."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class IdMixin:
    # UUID em vez de número sequencial: não revela quantos registros existem
    # nem permite "adivinhar" o próximo id.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class CriadoEmMixin:
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
