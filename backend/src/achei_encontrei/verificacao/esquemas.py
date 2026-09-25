import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from achei_encontrei.verificacao.dominio import StatusContestacao, TipoDocumento


class DevolucaoCriar(BaseModel):
    operador_id: uuid.UUID
    reivindicante_nome: str = Field(min_length=2, max_length=120)
    reivindicante_contato: str = Field(min_length=5, max_length=160)
    tipo_documento_conferido: TipoDocumento
    verificacao_resumo: str = Field(
        max_length=2000,
        description="O que a pessoa descreveu e o que o operador conferiu (ex.: sinais privados).",
    )
    achadego_registrado: bool = False


class DevolucaoLer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    achado_id: uuid.UUID
    custodia_id: uuid.UUID
    match_id: uuid.UUID | None
    operador_id: uuid.UUID
    reivindicante_nome: str
    tipo_documento_conferido: TipoDocumento
    verificacao_resumo: str
    achadego_registrado: bool
    status_contestacao: StatusContestacao
    realizada_em: datetime


class ContestacaoCriar(BaseModel):
    motivo: str = Field(min_length=10, max_length=2000)
