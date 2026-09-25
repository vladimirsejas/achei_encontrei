async def test_raiz_leva_ao_painel(cliente):
    r = await cliente.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/painel/"


async def test_painel_e_seus_arquivos_sao_servidos(cliente):
    pagina = await cliente.get("/painel/")
    assert pagina.status_code == 200
    assert "Hoje no balcão" in pagina.text
    for arquivo in ("estilo.css", "painel.js"):
        assert (await cliente.get(f"/painel/{arquivo}")).status_code == 200
