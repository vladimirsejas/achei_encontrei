async def test_trilha_por_instituicao(cliente, hub, registrar):
    await registrar()
    await registrar()
    r = await cliente.get("/eventos", params={"instituicao_id": hub["instituicao"]["id"]})
    tipos = [e["tipo"] for e in r.json()]
    assert tipos.count("ACHADO_CRIADO") == 2
    assert tipos.count("CUSTODIA_INICIADA") == 2


async def test_nao_existe_rota_para_apagar_eventos(cliente):
    r = await cliente.delete("/eventos")
    assert r.status_code == 405  # método não permitido
