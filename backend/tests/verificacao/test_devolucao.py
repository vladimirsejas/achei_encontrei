from tests.conftest import tipos_de_evento


def corpo(hub, documento="RG", resumo="Descreveu o adesivo de banda na parte de trás"):
    return {
        "operador_id": hub["operador"]["id"],
        "reivindicante_nome": "Maria",
        "reivindicante_contato": "maria@exemplo.com",
        "tipo_documento_conferido": documento,
        "verificacao_resumo": resumo,
    }


async def test_devolucao_encerra_custodia_e_gera_eventos(cliente, hub, registrar):
    achado = await registrar(categoria="ELETRONICO")
    r = await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub))
    assert r.status_code == 201
    assert "reivindicante_contato" not in r.json()  # contato não volta na resposta

    final = (await cliente.get(f"/achados/{achado['id']}")).json()
    assert final["estado"] == "DEVOLVIDO"
    assert final["custodia"]["destino"] == "DEVOLUCAO_DIRETA"
    assert "VERIFICACAO_APROVADA" in await tipos_de_evento(cliente, achado["id"])


async def test_documento_exige_identificacao_do_reivindicante(cliente, hub, registrar):
    achado = await registrar(categoria="DOCUMENTO")
    sem_doc = await cliente.post(
        f"/achados/{achado['id']}/devolucao", json=corpo(hub, documento="NENHUM")
    )
    assert sem_doc.status_code == 409
    com_doc = await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub))
    assert com_doc.status_code == 201


async def test_risco_medio_exige_descricao_detalhada(cliente, hub, registrar):
    achado = await registrar(categoria="CARTEIRA")
    r = await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub, resumo="é meu"))
    assert r.status_code == 409


async def test_nao_devolve_duas_vezes(cliente, hub, registrar):
    achado = await registrar(categoria="CHAVE")
    await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub))
    segunda = await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub))
    assert segunda.status_code == 409


async def test_contestacao_preserva_o_historico(cliente, hub, registrar):
    achado = await registrar(categoria="ELETRONICO")
    dev = (await cliente.post(f"/achados/{achado['id']}/devolucao", json=corpo(hub))).json()
    r = await cliente.post(
        f"/devolucoes/{dev['id']}/contestacao",
        json={
            "motivo": "Outra pessoa apareceu com a nota fiscal do aparelho",
        },
    )
    assert r.json()["status_contestacao"] == "CONTESTADA"
    # O registro original continua lá, intacto
    assert (await cliente.get(f"/achados/{achado['id']}/devolucao")).json()["id"] == dev["id"]
    assert "REIVINDICACAO_CONTESTADA" in await tipos_de_evento(cliente, dev["id"])
