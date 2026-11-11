"""R53 (titular, 10/11/2026): a Sala de controle é a do PRÓPRIO SISTEMA em funcionamento — nenhum espelho ou réplica é
medido — e é atualizada a cada 15 minutos no máximo. E as correções da Fase A e da Fase B do parecer de 10/11/2026."""
import json
import re
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import ev, livro


def _raiz(tmp_path):
    raiz = tmp_path / "sv"
    (raiz / "dados").mkdir(parents=True)
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", raiz / "dados" / f"{n}.db")
    for d in ("config", "eldorado", "eventos", "workflows", "scripts", ".github", "skills", "verificacao", "estudos", "ponte", "testes"):
        if Path(d).exists():
            (raiz / d).symlink_to(Path(d).resolve())
    return raiz


# ------------------------------------------------------------------------------------------------ R53: a Sala da produção
def test_a_sala_publicada_e_a_medida_pela_producao(tmp_path):
    """O site publica a Sala e o mapa medidos pela produção (painel_vivo/), como estão; não mede nada na cópia."""
    from eldorado.base.painel import vivo
    from eldorado.base.painel.dados import gerar

    raiz = _raiz(tmp_path)
    r = vivo.medir_e_gravar(raiz, ciclo=7)
    assert r["indice_saude"] is not None
    medida = json.loads((raiz / "painel_vivo/sala_controle.json").read_text(encoding="utf-8"))
    assert medida["fonte"]["origem"] == "produção" and medida["fonte"]["ciclo"] == 7
    gerar(raiz / "site", raiz)
    sc = json.loads((raiz / "site/dados/sala_controle.json").read_text(encoding="utf-8"))
    mapa = json.loads((raiz / "site/dados/mapa_arquivos.json").read_text(encoding="utf-8"))
    assert sc["fonte"]["origem"] == "produção" and sc["em"] == medida["em"]                 # a mesma medição, como está
    assert sc["instrumentos"] == medida["instrumentos"] and sc["fonte"]["idade_min_na_publicacao"] is not None
    assert mapa["fonte"]["origem"] == "produção" and mapa["medido_em"] == json.loads((raiz / "painel_vivo/mapa_arquivos.json").read_text())["medido_em"]
    # o gerador do site não mede a Sala nem o mapa (nenhuma réplica medida)
    fonte = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert "sala_montar(" not in fonte and "medir(raiz" not in fonte and "from .vivo import publicar" in fonte


def test_sem_a_medicao_da_producao_a_sala_diz_isso(tmp_path):
    """Sem painel_vivo/, a Sala não troca por outra fonte: diz que aguarda a produção, sem número."""
    from eldorado.base.painel.vivo import publicar

    sc, mapa = publicar(tmp_path)
    assert sc["fonte"]["origem"] == "aguardando a produção" and sc["indice_saude"] is None and sc["em"] is None
    assert mapa["nos"] == [] and mapa["fonte"]["origem"] == "aguardando a produção"
    (tmp_path / "painel_vivo").mkdir()
    (tmp_path / "painel_vivo/sala_controle.json").write_text(json.dumps({"em": "x", "fonte": {"origem": "réplica"}}))
    (tmp_path / "painel_vivo/mapa_arquivos.json").write_text(json.dumps({"fonte": {"origem": "réplica"}}))
    assert publicar(tmp_path)[0]["fonte"]["origem"] == "aguardando a produção"       # outra origem nunca é publicada


def test_o_relogio_da_sala_a_cada_15_minutos_no_maximo():
    from eldorado.base.painel import vivo

    assert vivo.INTERVALO_MIN <= vivo.INTERVALO_MAX_MIN == 15 and vivo.INTERVALO_MIN * vivo.MAPA_A_CADA <= 15
    c = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "def sala_viva()" in c and 'name="sala"' in c and "medir_e_gravar(" in c       # o relógio próprio, na produção
    g = Path("scripts/gravar.sh").read_text(encoding="utf-8")
    assert re.search(r"for pasta in [^;]*painel_vivo", g) and "painel.yml/dispatches" in g  # gravada e publicada
    assert "--gravar-min 5" in Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")


def test_a_pagina_mostra_a_origem_a_idade_e_o_que_mudou():
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "Medida pela própria produção" in p and "nvMudou(" in p and "medição atrasada" in p and "Aguardando a medição da produção" in p
    assert "atualiza a cada passagem do maestro" not in p


def test_o_que_mudou_entre_duas_medicoes():
    from eldorado.base.painel.vivo import mudancas

    a = {"em": "t0", "indice_saude": 70, "instrumentos": [{"id": "x", "nome": "X", "estado": "vermelho"}, {"id": "y", "nome": "Y", "estado": "verde"}],
         "anunciadores": [{"id": "al-1", "nome": "A"}, {"id": "al-2", "nome": "B"}]}
    b = {"em": "t1", "indice_saude": 81, "instrumentos": [{"id": "x", "nome": "X", "estado": "verde"}, {"id": "y", "nome": "Y", "estado": "amarelo"}],
         "anunciadores": [{"id": "al-2", "nome": "B"}]}
    m = mudancas(a, b)
    assert [x["id"] for x in m["melhoraram"]] == ["x"] and [x["id"] for x in m["pioraram"]] == ["y"]
    assert m["alarmes_apagados"] == 1 and "70 → 81" in m["resumo"]


# ------------------------------------------------------------------------------------------------ Fase A do parecer
def test_a_triagem_do_sistema_nao_passa_pela_entrega_do_chrome():
    """Passo 1: a triagem aprendida chama a importação sem a conferência da entrega completa (R41 é do Chrome)."""
    s = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert '"lote": "triagem-aprendida"' in s and "exigir_completo=False" in s and "TRIAGEM_MAXIMO" in s
    r = Path("eldorado/base/cerebro/rede.py").read_text(encoding="utf-8")
    assert "NOT LIKE '[triagem aprendida%'" in r                                          # a rede não aprende a própria regra


def test_a_chave_de_um_livro_excluido_nao_cria_outro_livro(bancos, gravador, diario, tmp_path):
    """Passo 2: o achado com a chave de um livro excluído não gera livro.criado (era recusado e derrubava 11 eventos)."""
    from eldorado.base.cartorio.indice import FORA, Indice
    from eldorado.base.missao.oportunidades import MissaoOportunidades
    from eldorado.base.nucleo.contratos import Achado

    missao = MissaoOportunidades()
    a = Achado(id="a1", motor="m", encontrado_em="2026-11-09", link_divulgacao="https://x.br/p", titulo="Prêmio Nacional de Inovação", dados={})
    chave = missao.chave(a)
    assert gravador.aplicar([livro(id="op-1", chave=chave, titulo="Prêmio Nacional de Inovação"),
                             ev("livro.excluido_logicamente", id="op-1", justificativa_exclusao="descartado", atualizado_em="2026-11-01")]).ok
    idx = Indice(bancos["biblioteca"], missao, diario)
    lid, novo, como = idx.resolver(a)
    assert lid == "op-1" and not novo and como.startswith(FORA)
    from eldorado.base.nucleo.eventos import ler
    assert not [e for e in ler(tmp_path / "eventos") if e.tipo == "livro.criado" and e.dados.get("id") != "op-1"]


def test_o_prazo_so_vai_a_ficha_que_existe():
    """Passo 3: o livro.prazo da auditoria só sai quando a ficha (livro_dados) do livro já existe."""
    s = Path("eldorado/base/cartorio/auditoria.py").read_text(encoding="utf-8")
    assert 'if lv["id"] in fim:\n                diario.emitir("livro.prazo"' in s


def test_os_dependentes_do_livro_recusado_sao_dispensados(bancos, gravador):
    """Passo 4: a criação recusada por chave repetida não derruba os eventos seguintes do livro em alarmes."""
    r = gravador.aplicar([livro(id="L-a", chave="k"), livro(id="L-b", chave="k"),
                          ev("livro.situacao", id="L-b", situacao="em trabalho", atualizado_em="2026-11-09"),
                          ev("livro.links", id="L-b", link_divulgacao="https://x", link_oficial=None, atualizado_em="2026-11-09")])
    assert [t for _e, t, _m in r.recusados] == ["livro.criado"] and r.dispensados >= 2
    abertos = bancos["cerebro"].execute("SELECT mensagem FROM alarme WHERE fechado_em IS NULL").fetchall()
    assert len(abertos) == 1 and "livro.criado" in abertos[0][0]


def test_os_alarmes_que_nunca_fechavam_sao_revistos():
    """Passo 4: a carga do Comandante, o motor preso que voltou a ler, o voo que caiu e a triagem recusada."""
    from eldorado.base.cerebro.revisao_alarmes import revisar

    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE execucao_passo(no TEXT, estado TEXT, em TEXT); CREATE TABLE maquina(em TEXT, processador REAL, memoria REAL);"
                    "CREATE TABLE alarme(id INTEGER, modulo TEXT, mensagem TEXT, aberto_em TEXT, fechado_em TEXT);"
                    "CREATE TABLE execucao_motor(motor TEXT, inicio TEXT, fim TEXT, erro TEXT);"
                    "CREATE TABLE comandante_decisao(etapa TEXT, em TEXT, recompensa REAL);")
    c.executemany("INSERT INTO alarme VALUES (?,?,?,?,NULL)", [
        (1, "comandante:carga", "a carga está acima de 85% há mais de 10 minutos (86%)", "2026-10-28T05:24"),
        (2, "regencia:coleta", "motor(es) preso(s) além do orçamento da coleta, abandonado(s) nesta passagem: sistema-s", "2026-11-09T23:06"),
        (3, "piloto:interceptador", "o voo da vaga 1 falhou: CalamineError", "2026-11-02T20:12"),
        (4, "analise-externa", "veredito recusado (R41, nada parcial): o lote triagem-aprendida não está em verificacao/lotes", "2026-11-04T21:50"),
        (5, "regencia:coleta", "motor(es) preso(s) além do orçamento da coleta, abandonado(s) nesta passagem: dou", "2026-11-09T23:06")])
    c.executemany("INSERT INTO maquina VALUES (?,?,?)", [(f"2026-11-0{i}T00:00", 0.5, 0.7) for i in range(1, 4)])
    c.execute("INSERT INTO execucao_motor VALUES ('sistema-s', '2026-11-10T01:00', '2026-11-10T01:20', NULL)")
    c.execute("INSERT INTO comandante_decisao VALUES ('interceptador', '2026-11-03T00:00', 1.0)")
    assert sorted(a for a, _ in revisar(c)) == [1, 2, 3, 4]                              # o dou não voltou a ler: fica aceso


def test_o_mapa_do_site_tolerante():
    """Passo 5: espaço antes da declaração, prefixo sem namespace, HTML no lugar do mapa e XML defeituoso."""
    from eldorado.motores.descoberta.estrutura_site import ler_mapa

    assert ler_mapa(b'\n<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://a.br/x</loc>'
                    b'<lastmod>2026-11-01</lastmod></url></urlset>') == ("urlset", [("https://a.br/x", "2026-11-01")])
    assert ler_mapa(b'<urlset><url><loc>https://a.br/y</loc><image:image><image:loc>i</image:loc></image:image></url></urlset>')[1] == [("https://a.br/y", None)]
    assert ler_mapa(b"<!doctype html><html>404</html>") == (None, [])                  # site sem mapa: não é erro
    assert ler_mapa(b'\xef\xbb\xbf<sitemapindex><sitemap><loc>https://a.br/s.xml</loc></sitemap></sitemapindex>') == ("indice", [("https://a.br/s.xml", None)])
    assert ler_mapa(b"<urlset><url><loc>https://a.br/a?x=1&y=2</loc></url></urlset>")[1] == [("https://a.br/a?x=1&y=2", None)]


def test_o_motor_novo_fica_em_carencia():
    """Passo 6: «nunca entregou» só depois de 7 dias de leitura; antes, em carência (atenção), não vermelho."""
    from eldorado.base.cerebro.sinais_motores import sinais

    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE motor_fonte(motor TEXT, nome TEXT, leituras INT, sem_mudanca INT, falhas INT, ultimo_erro TEXT, ultima TEXT, situacao TEXT);"
                    "CREATE TABLE motor_entregue(motor TEXT, em TEXT); CREATE TABLE execucao_motor(motor TEXT, inicio TEXT);")
    agora = datetime(2026, 11, 10, tzinfo=timezone.utc)
    for m, ini in (("novo", agora - timedelta(days=1)), ("velho", agora - timedelta(days=20))):
        c.execute("INSERT INTO motor_fonte VALUES (?, 'f', 3, 1, 0, NULL, ?, 'lida')", (m, (agora - timedelta(hours=2)).isoformat()))
        c.execute("INSERT INTO execucao_motor VALUES (?, ?)", (m, ini.isoformat()))
    n = sinais(c, "novo", ["f"], False, agora, False)
    v = sinais(c, "velho", ["f"], False, agora, False)
    assert n["luz"] == "amarelo" and n["em_carencia"] and not n["nunca_entregou"] and n["sinais"][0].startswith("em carência")
    assert v["luz"] == "vermelho" and v["nunca_entregou"]


# ------------------------------------------------------------------------------------------------ Fase B do parecer
def test_o_comandante_medido_pela_politica_em_vigor():
    """Passo 8: só a política em vigor (Thompson), pelo valor esperado com a inclusão de todos os motores."""
    from eldorado.base.aprendizado.avaliar import comparacao

    bib, cer = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    bib.execute("CREATE TABLE achado(motor TEXT, encontrado_em TEXT, decisao TEXT)")
    cer.execute("CREATE TABLE comandante_decisao(alvo TEXT, em TEXT, etapa TEXT, politica TEXT, recompensa REAL, contexto TEXT)")
    cer.execute("CREATE TABLE execucao_motor(motor TEXT, inicio TEXT)")
    hoje = datetime.now(timezone.utc).date().isoformat()
    for m in ("a", "b", "c", "d"):
        cer.execute("INSERT INTO execucao_motor VALUES (?, ?)", (m, hoje + "T01:00"))
    bib.executemany("INSERT INTO achado VALUES (?, ?, 'aceito')", [("a", hoje), ("b", hoje)])
    inc = json.dumps({"inclusao": {"a": 0.5, "b": 0.5, "c": 0.5, "d": 0.5}})
    cer.execute("INSERT INTO comandante_decisao VALUES ('a', ?, 'coleta', 'thompson', 1, ?)", (hoje + "T02:00", inc))
    cer.execute("INSERT INTO comandante_decisao VALUES ('c', ?, 'coleta', 'vw-squarecb', 0, NULL)", (hoje + "T02:00",))   # a antiga não conta
    r = comparacao(bib, cer, k=2)
    assert r["politica"] == "thompson" and r["decisoes"] == 1 and r["comandante"] == 0.5 and r["comandante_realizado"] == 1.0
    assert r["dias_valor_esperado"] == 1 and r["ordem_fixa"] == 0.5


def test_a_rede_pelos_ultimos_500_rotulos_e_o_acerto_dos_50():
    """Passo 9: a janela por contagem (os lotes não fazem a métrica saltar) e o acerto nos 50 de maior nota."""
    from eldorado.base.cerebro.rede import metricas_por_contagem

    assert metricas_por_contagem([("2026-11-01", True, 0.9)] * 10, 0.5)["discernimento"] is None   # menos de 300: não mede
    h = [(f"2026-11-{1 + i % 9:02d}T{i % 24:02d}", i % 3 == 0, 0.9 if i % 3 == 0 else 0.2) for i in range(800)]
    m = metricas_por_contagem(h, 0.5)
    assert m["amostras"] == 500 and m["acerto_50"] == 1.0 and m["precisao"] == 1.0
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert "rede:oportunidade:500" in s and '"rn_acerto_50"' in s and '"rn_rotulos"' in s


def test_o_mapa_separa_a_causa_propria_da_herdada():
    """Passo 10: a R45 continua (âmbar se algum usuário falha), e o mapa diz se o âmbar é herdado."""
    s = Path("eldorado/base/cerebro/mapa_arquivos.py").read_text(encoding="utf-8")
    assert s.count("herdado.add(p)") == 2 and '{"h": 1}' in s
    assert "âmbar herdado de quem usa" in Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")


def test_o_prazo_antes_da_ficha_e_dispensado(bancos, gravador):
    """Passo 3: o livro.prazo que chega antes da ficha (livro_dados) é dispensado, sem alarme; a ficha traz o prazo."""
    r = gravador.aplicar([livro(id="L-p", chave="kp"), ev("livro.prazo", livro_id="L-p", situacao_prazo="encerrada")])
    assert r.ok and r.dispensados == 1
    assert bancos["cerebro"].execute("SELECT COUNT(*) FROM alarme WHERE fechado_em IS NULL").fetchone()[0] == 0
