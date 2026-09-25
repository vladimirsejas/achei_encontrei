import uuid

from pydantic import BaseModel, ConfigDict, Field

from achei_encontrei.identidade.dominio import NivelAcesso, TipoInstituicao


class InstituicaoCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=160)
    tipo: TipoInstituicao
    cidade: str = Field(min_length=2, max_length=120)


class InstituicaoLer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    nome: str
    tipo: TipoInstituicao
    cidade: str
    hub_custodia: bool


class OperadorCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    contato: str = Field(min_length=5, max_length=160, description="E-mail ou telefone")
    nivel_acesso: NivelAcesso = NivelAcesso.BASICO


class OperadorLer(BaseModel):
    id: uuid.UUID
    instituicao_id: uuid.UUID
    nome: str
    nivel_acesso: NivelAcesso
    ativo: bool
