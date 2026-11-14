"""R55 (titular, 14/11/2026): as correções fixas do parecer de rotas dos pilotos — cada uma falha sem a correção."""
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.cerebro.relatorio_turno import gerar, medir
from eldorado.base.comandante.pilotos import _janela_espiao
from eldorado.motores.acesso import completa
from eldorado.motores.acesso.escada import Bloqueado, Resposta, avaliar
from eldorado.motores.acesso.ponte_br import assinar
from eldorado.motores.descoberta.metabusca import ROTAS_GERAIS, Metabusca
from eldorado.motores.descoberta.pistas import Pista
from eldorado.motores.pilotos.espiao import Espiao

PAG = {"https://fundacaoalfa.org/editais": ("Editais abertos", "lista de editais"),
       "https://fundacaoalfa.org/edital-2026.pdf": ("Edital Fundação Alfa 2026", "Edital: inscrições abertas para organizações da sociedade civil sem fins lucrativos."),
       "https://institutodelta.org.br/edital": ("Edital Instituto Delta", "Edital: inscrições abertas para organizações da sociedade civil sem fins lucrativos.")}


def _esp(tmp_path, consultar, **kw):
    return Espiao(tmp_path / "cerebro.db", consultar, lambda u: PAG.get(u), rnd=random.Random(1), **kw)


def test_o_espiao_nao_chama_a_rota_do_pncp():
    nomes = [n for n, _ in Metabusca(buscar=lambda u: None, tematicas=False).rotas("edital para OSC")]
    assert "pncp" not in nomes and "querido-diario" not in nomes
    assert "pncp" in [n for n, _ in Metabusca(buscar=lambda u: None).rotas("edital para OSC")]       # o Interceptador mantém


def test_o_descanso_so_na_falha_com_os_minutos_da_metabusca(tmp_path):
    e = _esp(tmp_path, lambda q: ([], ["searxng: falhou (Erro); descansa 1 min", "ddgs-bing: descansando", "marginalia: 0 pista(s), 0 nova(s)"]))
    e.missao()
    rotas = dict(e.con.execute("SELECT nome, descansa_ate FROM espiao_rota"))
    assert set(rotas) == {"searxng"}                                                    # «descansando» não regrava
    assert datetime.fromisoformat(rotas["searxng"]) < datetime.now(timezone.utc) + timedelta(minutes=2)   # 1 min, não 2 h


def test_o_verificador_nao_ve_captcha_na_resposta_json():
    avaliar(Resposta("http://localhost:8888/search?q=x", 200, b'{"results": [{"title": "Edital", "content": "resolva o captcha"}]}', "application/json"))
    try:
        avaliar(Resposta("https://x.org/", 200, b"<html><body>Please solve the captcha to continue</body></html>", "text/html"))
        raise AssertionError("a página de desafio em HTML deveria ser bloqueio")
    except Bloqueado:
        pass


def test_a_janela_conta_so_as_rotas_gerais(tmp_path):
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE espiao_rota (nome TEXT PRIMARY KEY, descansa_ate TEXT)")
    depois = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    c.executemany("INSERT INTO espiao_rota VALUES (?, ?)", [(r, depois) for r in ROTAS_GERAIS])
    c.execute("INSERT INTO espiao_rota VALUES ('pncp', NULL)")                         # a rota do PNCP livre não abre a janela
    assert not _janela_espiao(c)
    c.execute("UPDATE espiao_rota SET descansa_ate = NULL WHERE nome = 'marginalia'")
    assert _janela_espiao(c)


def test_a_pagina_barrada_nao_volta_por_30_dias(tmp_path):
    link = "https://institutodelta.org.br/edital"
    e = _esp(tmp_path, lambda q: ([Pista(titulo="Delta", link=link, origem="busca")], ["ddgs-bing: 1 pista(s), 1 nova(s)"]))
    aid = f"espiao-{__import__('hashlib').sha1(link.encode()).hexdigest()[:12]}"
    e.con.execute("INSERT INTO decisao_pertinencia(etapa, referencia, decisao, motivo, em) VALUES ('espiao', ?, 'barrado', 'listagem', ?)",
                  (aid, datetime.now(timezone.utc).isoformat()))
    e.con.commit()
    e2 = _esp(tmp_path, e.consultar)
    m = e2.missao()
    assert m["achados"] == [] and m["motivos"].get("barrada pela Pertinência nos últimos 30 dias") == 1


def test_a_listagem_e_aberta_e_cada_edital_entra_separado(tmp_path):
    e = _esp(tmp_path, lambda q: ([Pista(titulo="Editais", link="https://fundacaoalfa.org/editais", origem="busca")], ["ddgs-bing: 1 pista(s), 1 nova(s)"]),
             abrir_listagem=lambda u: ["https://fundacaoalfa.org/edital-2026.pdf"])
    m = e.missao()
    assert [a.link_oficial for a in m["achados"]] == ["https://fundacaoalfa.org/edital-2026.pdf"] and m["motivos"]["listagem aberta"] == 1


def test_a_varredura_do_cadastro(tmp_path):
    e = _esp(tmp_path, lambda q: ([], []))
    v = e.varredura(["institutodelta.org.br"], n=1)
    assert [a.link_divulgacao for a in v["achados"]] == ["https://institutodelta.org.br/edital"]


def test_o_relatorio_de_turno_e_gerado(tmp_path):
    e = _esp(tmp_path, lambda q: ([], ["searxng: falhou (Erro); descansa 1 min", "ddgs-bing: 3 pista(s), 3 nova(s)"]))
    desde = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    e.missao()
    r = medir(e.con, None, desde)
    assert r["missoes"] == 1 and r["placar"]["ddgs-bing"]["pistas"] == 3 and r["placar"]["searxng"]["falhou"] == 1 and r["pncp_nas_missoes"] == 0
    md = gerar(e.con, None, tmp_path, desde)
    assert md.parent == tmp_path / "relatorios" / "espiao" and md.with_suffix(".json").exists()


def test_o_degrau_9_nao_esta_na_escada_dos_pilotos():
    assert "local" not in completa.ORDEM


def test_a_ponte_do_espiao_assina_o_modo_e_nao_menciona_o_github():
    assert assinar("c" * 30, 1, "https://x.org/", "espiao") != assinar("c" * 30, 1, "https://x.org/")
    php = Path("ponte/ponte.php").read_text(encoding="utf-8")
    assert "TETO_ESPIAO" in php and "github" not in php.lower()


def test_a_sala_mede_os_achados_aceitos_do_espiao():
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert '"Achados do Espião aceitos em 7 dias"' in s and '"Missões do Espião em 24 h",\n            miss,' not in s
