async def test_criar_instituicao_e_operadores(cliente, hub):
    inst_id = hub["instituicao"]["id"]
    ops = (await cliente.get(f"/instituicoes/{inst_id}/operadores")).json()
    assert len(ops) == 1
    assert ops[0]["nome"] == "Ana do Balcão"
    assert "contato" not in ops[0]


async def test_instituicao_inexistente_da_404(cliente):
    r = await cliente.get("/instituicoes/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
