from datetime import date, timedelta

from tests.conftest import tipos_de_evento


async def test_registro_cria_achado_custodia_e_eventos(cliente, hub, registrar):
    achado = await registrar(categoria="DOCUMENTO", achadego_informado=True)
    assert achado["estado"] == "EM_CUSTODIA"
    assert achado["nivel_risco"] == "ALTO"
    assert achado["prazo_legal_entrega"] == str(date.today() + timedelta(days=15))
    assert achado["custodia"]["responsavel_tipo"] == "INSTITUICAO"
    assert achado["custodia"]["local_fisico"] == "Armário 3 do balcão"
    assert await tipos_de_evento(cliente, achado["id"]) == ["ACHADO_CRIADO", "ACHADEGO_INFORMADO"]


async def test_operador_de_outra_instituicao_e_barrado(cliente, hub):
    outra = (
        await cliente.post(
            "/instituicoes",
            json={
                "nome": "Hotel Vizinho",
                "tipo": "HOTEL",
                "cidade": "Rio Claro",
            },
        )
    ).json()
    r = await cliente.post(
        f"/instituicoes/{outra['id']}/achados",
        json={
            "operador_id": hub["operador"]["id"],  # operador do shopping!
            "descricao": "Tentativa indevida",
            "categoria": "CHAVE",
            "local_encontrado": "Recepção",
            "data_achado": str(date.today()),
            "local_guarda": "Gaveta",
        },
    )
    assert r.status_code == 403


async def test_visao_publica_nao_mostra_detalhes(cliente, hub, registrar):
    await registrar()
    publicos = (
        await cliente.get(f"/instituicoes/{hub['instituicao']['id']}/achados/publicos")
    ).json()
    assert len(publicos) == 1
    assert set(publicos[0]) == {"id", "categoria", "data_achado"}


async def test_transferencia_registra_de_e_para(cliente, hub, registrar):
    achado = await registrar()
    op_id = hub["operador"]["id"]
    r = await cliente.post(
        f"/achados/{achado['id']}/transferencias",
        json={
            "operador_id": op_id,
            "para_tipo": "OPERADOR",
            "para_id": op_id,
            "local_fisico": "Cofre da administração",
            "motivo": "Objeto de valor: guardar no cofre",
        },
    )
    assert r.status_code == 201
    assert r.json()["de_tipo"] == "INSTITUICAO"
    atual = (await cliente.get(f"/achados/{achado['id']}")).json()
    assert atual["custodia"]["local_fisico"] == "Cofre da administração"
    assert len((await cliente.get(f"/achados/{achado['id']}/transferencias")).json()) == 1


async def test_alerta_de_prazo_e_emitido_uma_unica_vez(cliente, hub, registrar):
    velho = await registrar(dias_atras=11)
    await registrar(dias_atras=2)  # ainda no prazo: não deve gerar alerta
    assert (await cliente.post("/prazos/verificar")).json() == {"alertas_emitidos": 1}
    assert (await cliente.post("/prazos/verificar")).json() == {"alertas_emitidos": 0}
    assert "PRAZO_ENTREGA_PROXIMO_DO_LIMITE" in await tipos_de_evento(cliente, velho["id"])


async def test_sistema_nunca_encaminha_sozinho_e_operador_registra_entrega(cliente, hub, registrar):
    vencido = await registrar(dias_atras=20)
    await cliente.post("/prazos/verificar")
    ainda = (await cliente.get(f"/achados/{vencido['id']}")).json()
    assert ainda["estado"] == "EM_CUSTODIA"  # o sistema alertou, mas não agiu sozinho

    prazos = (await cliente.get(f"/instituicoes/{hub['instituicao']['id']}/prazos")).json()
    assert prazos[0]["situacao"] == "VENCIDO"

    r = await cliente.post(
        f"/achados/{vencido['id']}/entrega-autoridade",
        json={
            "operador_id": hub["operador"]["id"],
            "orgao": "Delegacia de Polícia de Rio Claro",
            "protocolo": "BO-123",
        },
    )
    assert r.json()["estado"] == "ENCAMINHADO_AUTORIDADE"
    final = (await cliente.get(f"/achados/{vencido['id']}")).json()
    assert final["custodia"]["destino"] == "AUTORIDADE_COMPETENTE"
    assert final["custodia"]["encerrada_em"] is not None


async def test_relatorio_da_instituicao(cliente, hub, registrar):
    a1 = await registrar(categoria="CHAVE")
    await registrar(categoria="ELETRONICO", dias_atras=12)
    vencido = await registrar(categoria="CARTEIRA", dias_atras=20)
    op = hub["operador"]["id"]
    await cliente.post(
        f"/achados/{a1['id']}/devolucao",
        json={
            "operador_id": op,
            "reivindicante_nome": "João",
            "reivindicante_contato": "joao@x.com",
            "tipo_documento_conferido": "NENHUM",
            "verificacao_resumo": "Descreveu o chaveiro azul",
        },
    )
    await cliente.post(
        f"/achados/{vencido['id']}/entrega-autoridade",
        json={
            "operador_id": op,
            "orgao": "Delegacia",
        },
    )
    rel = (await cliente.get(f"/instituicoes/{hub['instituicao']['id']}/relatorio")).json()
    assert rel["total_registrados"] == 3
    assert rel["devolvidos"] == 1
    assert rel["encaminhados_autoridade"] == 1
    assert rel["em_custodia"] == 1
    assert rel["taxa_devolucao_percentual"] == 50.0
    assert rel["prazos_proximos_do_limite"] == 1
