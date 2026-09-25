import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from achei_encontrei.itens.dominio import (
    Categoria,
    DestinoCustodia,
    EstadoAchado,
    NivelRisco,
    SituacaoPrazo,
    TipoResponsavel,
)


class AchadoRegistrarNoBalcao(BaseModel):
    operador_id: uuid.UUID
    descricao: str = Field(min_length=5, max_length=2000)
    sinais_privados: str | None = Field(
        default=None,
        max_length=2000,
        description="Detalhes que só o dono saberia. Nunca são exibidos publicamente.",
    )
    categoria: Categoria
    local_encontrado: str = Field(min_length=2, max_length=200)
    data_achado: date
    local_guarda: str = Field(
        min_length=2, max_length=200, description="Onde o objeto fica guardado no hub"
    )
    achadego_informado: bool = Field(
        default=False,
        description="Quem encontrou foi informado do direito ao achádego (CC art. 1.234)?",
    )

    @field_validator("data_achado")
    @classmethod
    def nao_no_futuro(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("A data do achado não pode estar no futuro.")
        return v


class CustodiaLer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    responsavel_tipo: TipoResponsavel
    responsavel_id: uuid.UUID
    local_fisico: str
    iniciada_em: datetime
    encerrada_em: datetime | None
    destino: DestinoCustodia | None


class AchadoOperador(BaseModel):
    """Visão completa, para o operador da instituição (inclui os sinais privados)."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    instituicao_id: uuid.UUID | None
    registrado_por_operador_id: uuid.UUID | None
    descricao: str
    sinais_privados: str | None
    categoria: Categoria
    nivel_risco: NivelRisco
    local_encontrado: str
    data_achado: date
    prazo_legal_entrega: date
    achadego_informado: bool
    estado: EstadoAchado
    criado_em: datetime


class AchadoComCustodia(AchadoOperador):
    custodia: CustodiaLer


class AchadoPublico(BaseModel):
    """Visão PÚBLICA (DOMAIN_MODEL, seção 5): só o suficiente para alguém se reconhecer.

    Sem descrição, sem fotos, sem sinais privados — que serão perguntados na verificação.
    """

    id: uuid.UUID
    categoria: Categoria
    data_achado: date


class TransferenciaCriar(BaseModel):
    operador_id: uuid.UUID
    para_tipo: TipoResponsavel
    para_id: uuid.UUID
    local_fisico: str = Field(min_length=2, max_length=200)
    motivo: str = Field(min_length=3, max_length=300)


class TransferenciaLer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    de_tipo: TipoResponsavel
    de_id: uuid.UUID
    para_tipo: TipoResponsavel
    para_id: uuid.UUID
    local_fisico: str
    motivo: str
    operador_id: uuid.UUID | None
    ocorrida_em: datetime


class EntregaAutoridadeCriar(BaseModel):
    operador_id: uuid.UUID
    orgao: str = Field(min_length=3, max_length=200, description="Ex.: Delegacia de Polícia")
    protocolo: str | None = Field(default=None, max_length=100)


class ItemPrazo(BaseModel):
    achado_id: uuid.UUID
    categoria: Categoria
    data_achado: date
    prazo_legal_entrega: date
    situacao: SituacaoPrazo
    dias_restantes: int


class RelatorioInstituicao(BaseModel):
    instituicao_id: uuid.UUID
    gerado_em: date
    total_registrados: int
    em_custodia: int
    devolvidos: int
    encaminhados_autoridade: int
    taxa_devolucao_percentual: float | None
    prazos_proximos_do_limite: int
    prazos_vencidos_sem_destino: int
    por_categoria: dict[str, int]
