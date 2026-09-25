"""Monta a aplicação: liga os módulos e trata os erros de domínio num só lugar."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from achei_encontrei.auditoria.rotas import rotas as rotas_auditoria
from achei_encontrei.compartilhado.erros import ErroDominio
from achei_encontrei.identidade.rotas import rotas as rotas_identidade
from achei_encontrei.itens.rotas import rotas_achados, rotas_balcao, rotas_prazos
from achei_encontrei.verificacao.rotas import rotas as rotas_verificacao

app = FastAPI(
    title="Achei, Encontrei — API",
    version="0.1.0",
    description="Balcão institucional de achados e perdidos: registro, custódia auditável, "
    "prazo legal, verificação proporcional ao risco e devolução.",
)

app.include_router(rotas_identidade)
app.include_router(rotas_balcao)
app.include_router(rotas_achados)
app.include_router(rotas_verificacao)
app.include_router(rotas_prazos)
app.include_router(rotas_auditoria)


@app.exception_handler(ErroDominio)
async def _erro_dominio(_: Request, exc: ErroDominio):
    return JSONResponse(status_code=exc.status_http, content={"detail": str(exc)})


@app.get("/saude", tags=["Infra"])
async def saude():
    return {"status": "ok"}
