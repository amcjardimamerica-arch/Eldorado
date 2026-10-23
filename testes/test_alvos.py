"""Os alvos (estudo da titular, 19/10/2026): pontos de captação vigiados dentro do motor do seu canal, com a previsão
de edição aprendida pelo próprio motor; a rota alternativa quando a principal falha; o registro recusa motor sem rota."""
import pytest
from servidor_local import criar_servidor

from eldorado.motores.canal.motor import CfgAlvo, Configuracao, MotorCanal

PAGINA = ("<html><body><main><h1>Fundo de Apoio à Cultura</h1><p>" + "Programa estadual de fomento cultural. " * 6 +
          '</p><a href="/editais/edital-7-2026.pdf">Edital de chamamento público nº 7/2026 — inscrições abertas</a></main></body></html>').encode()


@pytest.fixture
def site():
    paginas = {"/fundo": (200, PAGINA, "text/html; charset=utf-8"), "/editais/edital-7-2026.pdf": (404, b"", "text/plain")}
    srv, est = criar_servidor(paginas)
    yield f"http://127.0.0.1:{est.porta}", paginas
    srv.shutdown()


def config(tmp_path, base, previsao=None, enderecos=None):
    previsao = f"previsao_meses = {previsao}\n" if previsao else ""
    enderecos = enderecos or [f"{base}/fundo"]
    lista = ", ".join(f'"{u}"' for u in enderecos)
    (tmp_path / "m.toml").write_text(f"""[motor]
id = "teste-alvos"
nome = "Teste dos alvos"
categoria = "Executivo"
finalidade = "vigiar os pontos de captação do canal"
tipo_finalidade = "recorrencia"

[[alvo]]
id = "f260-teste-001"
nome = "Fundo de Apoio à Cultura"
enderecos = [{lista}]
{previsao}
[acesso]
degraus = ["api"]
intervalo_s = 0

[lexico]
termos = ["re:edital|chamamento"]
""", encoding="utf-8")
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_alvo_mudou_entrega_e_aprende_o_mes(site, tmp_path):
    base, paginas = site
    m = config(tmp_path, base)
    achados = list(m.buscar(None))
    assert [a.titulo for a in achados] == ["Edital de chamamento público nº 7/2026 — inscrições abertas"]
    assert len(m.estado.meses_do_alvo("f260-teste-001")) == 1
    assert list(m.buscar(None)) == [] and any("sem mudança" in r for r in m.relatorio)                    # a vigilância


def test_rota_alternativa_quando_a_principal_falha(site, tmp_path):
    base, _ = site
    m = config(tmp_path, base, enderecos=[f"{base}/fora-do-ar", f"{base}/fundo"])
    assert len(list(m.buscar(None))) == 1


def test_janela_prevista():
    m = object.__new__(MotorCanal)
    m.estado = type("E", (), {"meses_do_alvo": lambda self, a: []})()
    a = CfgAlvo(id="x", nome="x", enderecos=["https://x"], previsao_meses=[3])
    assert [mes for mes in range(1, 13) if MotorCanal._na_janela(m, a, mes)] == [2, 3, 4]
    assert MotorCanal._na_janela(m, CfgAlvo(id="y", nome="y", enderecos=["https://y"]), 7)                  # sem previsão: sempre


def test_o_registro_recusa_motor_sem_rota_ou_sem_finalidade():
    with pytest.raises(ValueError, match="sem nenhuma rota"):
        Configuracao(motor={"id": "x", "nome": "x", "categoria": "c", "finalidade": "f"})
    with pytest.raises(ValueError, match="sem finalidade"):
        Configuracao(motor={"id": "x", "nome": "x", "categoria": "c", "finalidade": " "}, fonte=[{"nome": "n", "url": "https://x"}])


def test_a_fabrica_segue_a_orientacao(tmp_path):
    from eldorado.motores.canal.fabrica import criar, ficha, validar
    assert "Diário Oficial do Estado de Goiás" in ficha("do-goias") and "alvos (2)" in ficha("do-goias")
    p = criar("do-goias", pasta=tmp_path)
    texto = p.read_text(encoding="utf-8")
    assert 'id = "do-goias"' in texto and 'categoria_estudo = "EXE"' in texto and "[[alvo]]" in texto and "bloqueios_conhecidos" in texto
    assert '# url = "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/"' in texto      # candidata, comentada
    r = dict((n, ok) for n, ok, _ in validar("do-goias", pasta=tmp_path))
    assert r["aceito pelo registro"] and r["conforme o estudo (categoria)"] and r["alvos do estudo"]
    with pytest.raises(FileExistsError):
        criar("do-goias", pasta=tmp_path)                                                                  # não se recria
