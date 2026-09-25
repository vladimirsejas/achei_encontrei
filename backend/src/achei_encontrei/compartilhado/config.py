"""Configurações lidas do arquivo .env (na raiz do projeto) ou de variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    # Procura o .env na raiz do projeto (quando rodamos de dentro de backend/) e no diretório atual.
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str = "postgresql+asyncpg://achei:achei@localhost:5432/achei_encontrei"

    # Código Penal, art. 169, parágrafo único, II: 15 dias para restituir ao dono
    # ou entregar à autoridade competente.
    prazo_legal_dias: int = 15
    # Dia em que o sistema avisa que o prazo está chegando ao fim.
    dias_alerta_prazo: int = 10


config = Configuracoes()
