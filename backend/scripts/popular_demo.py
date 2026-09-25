"""Popula o banco com um balcão de demonstração, para mostrar o sistema funcionando.

Uso (de dentro de backend/):  uv run python scripts/popular_demo.py
"""

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from achei_encontrei.compartilhado.banco import FabricaSessao
from achei_encontrei.identidade import servicos as identidade
from achei_encontrei.identidade.esquemas import InstituicaoCriar, OperadorCriar
from achei_encontrei.identidade.modelos import Instituicao
from achei_encontrei.itens import servicos as itens
from achei_encontrei.itens.esquemas import AchadoRegistrarNoBalcao
from achei_encontrei.verificacao import servicos as verificacao
from achei_encontrei.verificacao.esquemas import DevolucaoCriar

NOME_DEMO = "Shopping Demonstração"

OBJETOS = [
    # (categoria, dias atrás, descrição, sinais privados, onde foi encontrado)
    (
        "CHAVE",
        1,
        "Molho com 3 chaves e chaveiro de borracha",
        "Chaveiro em forma de tartaruga verde",
        "Estacionamento G2",
    ),
    (
        "ELETRONICO",
        2,
        "Celular preto, tela intacta",
        "Capinha azul com adesivo de gato",
        "Praça de alimentação",
    ),
    (
        "BOLSA_MOCHILA",
        5,
        "Mochila escolar cinza",
        "Caderno com nome escrito na contracapa",
        "Cinema, sala 3",
    ),
    (
        "DOCUMENTO",
        11,
        "Documento de identidade dentro de capa plástica",
        "Foto 3x4 antiga atrás",
        "Banheiro do piso 1",
    ),
    (
        "CARTEIRA",
        17,
        "Carteira marrom de couro",
        "Bilhete de loteria dobrado no compartimento",
        "Corredor da loja âncora",
    ),
]


async def main() -> None:
    async with FabricaSessao() as sessao:
        existe = await sessao.scalar(select(Instituicao).where(Instituicao.nome == NOME_DEMO))
        if existe:
            print(f"O '{NOME_DEMO}' já existe (id {existe.id}). Nada foi alterado.")
            return

        hub = await identidade.criar_instituicao(
            sessao, InstituicaoCriar(nome=NOME_DEMO, tipo="SHOPPING", cidade="Rio Claro")
        )
        operadora = await identidade.criar_operador(
            sessao, hub.id, OperadorCriar(nome="Ana (balcão)", contato="balcao@demo.com")
        )

        registrados = []
        for categoria, dias, descricao, sinais, local in OBJETOS:
            achado, _ = await itens.registrar_achado_no_balcao(
                sessao,
                hub.id,
                AchadoRegistrarNoBalcao(
                    operador_id=operadora.id,
                    descricao=descricao,
                    sinais_privados=sinais,
                    categoria=categoria,
                    local_encontrado=local,
                    data_achado=date.today() - timedelta(days=dias),
                    local_guarda="Armário do balcão de informações",
                    achadego_informado=True,
                ),
            )
            registrados.append(achado)

        # A dona da chave aparece no balcão e descreve o chaveiro de tartaruga.
        await verificacao.registrar_devolucao(
            sessao,
            registrados[0].id,
            DevolucaoCriar(
                operador_id=operadora.id,
                reivindicante_nome="Cliente da demonstração",
                reivindicante_contato="cliente@demo.com",
                tipo_documento_conferido="NENHUM",
                verificacao_resumo="Descreveu o chaveiro de tartaruga verde sem ver o objeto",
            ),
        )

        alertas = await itens.verificar_prazos(sessao, date.today())
        rel = await itens.relatorio_instituicao(sessao, hub.id, date.today())

    print(f"\n✅ '{NOME_DEMO}' criado.  id da instituição: {hub.id}")
    print(f"   id da operadora Ana:  {operadora.id}")
    print(f"\n   Objetos registrados:        {rel.total_registrados}")
    print(f"   Em custódia:                {rel.em_custodia}")
    print(f"   Devolvidos:                 {rel.devolvidos}")
    print(f"   Alertas de prazo emitidos:  {alertas}")
    print(f"   Prazos vencidos sem destino: {rel.prazos_vencidos_sem_destino}")
    print("\nSuba o servidor e abra http://localhost:8000 para ver o balcão.")


if __name__ == "__main__":
    asyncio.run(main())
