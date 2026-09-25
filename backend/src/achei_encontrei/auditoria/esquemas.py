import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from achei_encontrei.auditoria.dominio import TipoEvento


class EventoLer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tipo: TipoEvento
    entidade: str
    entidade_id: uuid.UUID
    instituicao_id: uuid.UUID | None
    dados: dict
    ocorrido_em: datetime
