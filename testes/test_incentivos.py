"""Os motores de incentivo (o programa e a sua legislação) e a ferramenta de seguir até a fonte oficial."""
import re
from pathlib import Path

import pymupdf
import pytest
from conftest import AGORA, ev
from servidor_local import criar_servidor

from eldorado.base.cartorio.cartorio import Cartorio
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.eventos import ler
from eldorado.motores.canal.motor import MotorCanal
from eldorado.motores.descoberta import fonte_oficial


def pdf(texto):
    d = pymupdf.open()
    d.new_page().insert_textbox(pymupdf.Rect(40, 40, 555, 800), texto, fontsize=10)
    return d.tobytes()


POST = b"""<html><body><h1>Instituto abre o Edital n\xc2\xba 5/2026 de apoio a projetos sociais</h1>
<a href="https://facebook.com/instituto">Siga</a><a href="/files/relatorio-anual-2025.pdf">Relat\xc3\xb3rio anual</a>
<a href="/files/edital-5-2026-regulamento.pdf">Regulamento do Edital n\xc2\xba 5/2026</a></body></html>"""
PAGINAS = {"norma": "Instrução Normativa vigente: propostas de 1º de fevereiro a 31 de outubro. " * 3}


@pytest.fixture(scope="module")
def site():
    rotas = {"/post-edital-5": (200, POST, "text/html; charset=utf-8"),
             "/files/edital-5-2026-regulamento.pdf": (200, pdf("EDITAL Nº 5/2026. O presente edital tem por objeto o apoio a projetos sociais de organizações da sociedade civil."), "application/pdf"),
             "/files/relatorio-anual-2025.pdf": (200, pdf("Relatório anual"), "application/pdf"),
             "/lei-rouanet/legislacao": (200, lambda: ("<html><body><p>" + PAGINAS["norma"] + "</p></body></html>").encode(), "text/html; charset=utf-8"),
             "/lei-rouanet": (200, ("<html><body><p>" + "Lei Rouanet: incentivo a projetos culturais. " * 5 + "</p></body></html>").encode(), "text/html; charset=utf-8")}
    srv, estado = criar_servidor(rotas)
    yield f"http://127.0.0.1:{estado.porta}"
    srv.shutdown()


def test_candidatos_da_fonte_oficial():
    c = fonte_oficial.candidatos(POST, "https://inst.org/post", "Instituto abre o Edital nº 5/2026 de apoio a projetos sociais")
    assert c[0]["url"] == "https://inst.org/files/edital-5-2026-regulamento.pdf" and c[0]["pontos"] >= 9         # o número do edital pesa
    assert all("facebook" not in x["url"] for x in c)


def test_motor_segue_da_divulgacao_ao_documento_oficial(site, tmp_path):
    (tmp_path / "m.toml").write_text(f'''[motor]
id = "teste"
nome = "teste"
categoria = "teste"
finalidade = "teste"
[[fonte]]
nome = "lista"
url = "{site}/lista"
tipo = "api"
caminhos = {{ itens = "[*]", titulo = "t", link = "l" }}
[acesso]
intervalo_s = 0
[leitura]
seguir_oficial = true
''')
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "d", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    from eldorado.motores.descoberta.pistas import Pista
    achado = m._achado(m.cfg.fonte[0], Pista("Instituto abre o Edital nº 5/2026 de apoio a projetos sociais", f"{site}/post-edital-5", "teste"), 0)
    assert achado.link_oficial == f"{site}/files/edital-5-2026-regulamento.pdf" and achado.link_divulgacao == f"{site}/post-edital-5"
    assert "tem por objeto o apoio" in achado.documento["paginas"][0]


def motor_rouanet(site, tmp_path):
    texto = Path("eldorado/motores/canal/config/rouanet.toml").read_text(encoding="utf-8")
    texto = re.sub(r"https://www\.gov\.br/cultura/pt-br/assuntos/acoes-programas-e-politicas", site, texto)
    (tmp_path / "rouanet.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "rouanet.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_programa_entregue_com_a_lei_e_so_quando_a_norma_muda(site, tmp_path):
    achados = [a for a in motor_rouanet(site, tmp_path).buscar(None) if a.dados.get("fonte") == "programa"]
    assert len(achados) == 1
    a = achados[0]
    assert a.dados["leis"] == ["lei-8313-1991"] and a.link_oficial.endswith("/lei-rouanet/legislacao") and len(a.documento["paginas"]) == 2
    assert "1º de fevereiro a 31 de outubro" in a.documento["paginas"][0]
    assert [x for x in motor_rouanet(site, tmp_path).buscar(None) if x.dados.get("fonte") == "programa"] == []      # sem mudança
    PAGINAS["norma"] = "Nova Instrução Normativa: propostas de 1º de março a 30 de novembro. " * 3
    novos = [x for x in motor_rouanet(site, tmp_path).buscar(None) if x.dados.get("fonte") == "programa"]
    assert len(novos) == 1 and novos[0].id != a.id                                                                 # a norma mudou


def test_cartorio_liga_o_livro_a_lei(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar([ev("lei.registrada", id="lei-8313-1991", esfera="federal", ementa="Lei Rouanet", atualizada_em=AGORA)]).ok
    from eldorado.base.nucleo.contratos import Achado
    a = Achado(id="r1", motor="rouanet", encontrado_em="2026-10-22", link_divulgacao="https://x", titulo="Lei Rouanet (Lei 8.313/1991) — propostas no Salic",
               dados={"uf": "BR", "orgao": "Ministério da Cultura", "leis": ["lei-8313-1991", "lei-inexistente"]})
    import msgspec

    from eldorado.base.cerebro.regencia import achado_para_evento
    assert gravador.aplicar([ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="oportunidade")]).ok   # como no fluxo real
    Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])
    eventos = list(ler(tmp_path / "eventos"))
    assert [e.dados["lei_id"] for e in eventos if e.tipo == "livro.legislacao"] == ["lei-8313-1991"]
    assert any("lei-inexistente" in e.dados.get("mensagem", "") for e in eventos if e.tipo == "alarme.aberto")
    assert gravador.aplicar(eventos).ok
    assert [tuple(r) for r in bancos["biblioteca"].execute("SELECT lei_id, papel FROM livro_lei")] == [("lei-8313-1991", "rege o programa")]
