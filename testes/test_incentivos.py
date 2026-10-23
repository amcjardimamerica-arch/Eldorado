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
    texto = Path("eldorado/motores/canal/config/salic.toml").read_text(encoding="utf-8")
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


LEGISLACAO = """<html><body><main><h1>Legislação – Goyazes</h1><ul>
<li><a href="/l/lei-13613.pdf">Lei Nº 13.613, de 11 de maio de 2000</a></li><li><a href="/l/decreto-10302.pdf">DECRETO Nº 10.302, DE 12 DE AGOSTO DE 2023</a></li>
<li><a href="/l/res-1-2022.pdf">Resolução nº 001/2022 – de 19 de abril de 2022</a></li><li><a href="/l/res-5-2025.pdf">Resolução nº 05/2025, de 01 de julho de 2025</a></li>
<li><a href="/l/res-1-2026.pdf">Resolução nº 01/2026, de 12 de janeiro de 2026</a></li><li><a href="/l/in-1-2024.pdf">Instrução Normativa Nº 1/2024</a></li>
<li><a href="https://facebook.com/secult">Resolução no Facebook</a></li></ul></main></body></html>"""


def test_normas_mais_recentes_da_pagina_de_legislacao():
    n = fonte_oficial.normas_recentes(LEGISLACAO, "https://goias.gov.br/cultura/programa-goyazes/legislacao/", "resolucao|instrucao normativa|portaria", 3)
    assert [x["url"].rsplit("/", 1)[1] for x in n] == ["res-1-2026.pdf", "res-5-2025.pdf", "in-1-2024.pdf"]      # a lei e o decreto não são norma de prazo


def test_extracao_propria_do_motor_de_incentivo(tmp_path):
    m = MotorCanal("eldorado/motores/canal/config/estaduais-go-gov.toml", dados=tmp_path / "d", ponte=tmp_path / "p")
    r = m._extrair(["Lista de normas.", "RESOLUÇÃO Nº 01/2026. Art. 2º Os projetos culturais poderão ser apresentados no período de 12 de janeiro de 2026 "
                    "a 23 de março de 2026. Art. 5º O valor máximo por projeto não poderá ultrapassar R$ 500.000,00. Art. 7º Poderão apresentar projetos "
                    "pessoas físicas e jurídicas domiciliadas em Goiás há pelo menos dois anos."], m.cfg.programa.extracao)
    assert r["itens"]["Prazo de inscrição"]["valor"].endswith("12 de janeiro de 2026 a 23 de março de 2026") and r["itens"]["Prazo de inscrição"]["pagina"] == 2
    assert "R$ 500.000,00" in r["itens"]["Valor"]["valor"] and r["itens"]["Requisitos"]["valor"].startswith("Poderão apresentar projetos")
    assert "Resultado" in r["nao_certificar"]


def test_precedencia_a_validada_vale_e_o_conflito_e_contestado(gravador, bancos, diario, tmp_path):
    from datetime import date

    from eldorado.base.cartorio.auditoria import aplicar, auditar
    from eldorado.base.missao import itens as I
    assert I.melhor([{"id": 1, "item": "Resultado", "fase": "eldorado0", "valor": "30 dias"},
                     {"id": 9, "item": "Resultado", "fase": "certificacao", "valor": "23 de dezembro de 1991"}])["Resultado"]["valor"] == "30 dias"
    assert gravador.aplicar([ev("livro.criado", id="R", missao="oportunidades", chave="r", titulo="Lei Rouanet — propostas no Salic", uf="BR", estrela="sem",
                                selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
                             ev("certidao.gravada", livro_id="R", item="Resultado", valor="Portaria publicada no DOU em até 30 dias", fase="eldorado0",
                                situacao="comprovado", em=AGORA),
                             ev("certidao.gravada", livro_id="R", item="Resultado", valor="23 de dezembro de 1991", fase="certificacao", situacao="comprovado", em=AGORA)]).ok
    r = next(auditar(bancos["biblioteca"], date(2026, 10, 22)))
    assert any("conflita com a certidão validada" in x for x in r.contestadas)
    aplicar([r], diario)
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert dict(bancos["biblioteca"].execute("SELECT fase, situacao FROM certidao WHERE item='Resultado'").fetchall()) == {"eldorado0": "comprovado",
                                                                                                                            "certificacao": "contestado"}


def test_cartorio_usa_a_extracao_do_motor_e_respeita_o_nao_certificar(gravador, bancos, diario, tmp_path):
    import msgspec

    from eldorado.base.cerebro.regencia import achado_para_evento
    from eldorado.base.nucleo.contratos import Achado
    texto = "Lei de 23 de dezembro de 1991. O resultado final será publicado em 15/12/2026. " * 3
    a = Achado(id="g1", motor="goyazes", encontrado_em="2026-10-22", link_divulgacao="https://x", titulo="Programa Goyazes — incentivo fiscal à cultura em Goiás",
               dados={"uf": "GO", "orgao": "Secult", "nao_certificar": ["Resultado"],
                      "itens": {"Prazo de inscrição": {"valor": "de 12 de janeiro de 2026 a 23 de março de 2026", "trecho": "Art. 2º ...", "pagina": 2}}},
               documento={"url": "https://x/norma", "sha256": "sha-norma", "tipo": "html", "paginas": [texto]})
    assert gravador.aplicar([ev("documento.registrado", url="https://x/norma", sha256="sha-norma", obtido_em=AGORA, oficial=1),
                             ev("pagina.gravada", documento_sha256="sha-norma", numero=1, texto=texto),
                             ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="oportunidade")]).ok
    Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    c = dict(bancos["biblioteca"].execute("SELECT item, valor FROM certidao").fetchall())
    assert c["Prazo de inscrição"].startswith("de 12 de janeiro") and "Resultado" not in c
