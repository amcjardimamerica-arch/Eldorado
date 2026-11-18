"""As correções da manutenção de 16/11/2026 (o relatório de correções, fichas C-01 a C-25)."""
from eldorado.base.cerebro.encaminhamento import Encaminhamento
from eldorado.base.nucleo.contratos import Achado


class _D:
    def __init__(self):
        self.ev = []

    def emitir(self, t, m, d, **k):
        self.ev.append(t)


def test_o_no_originais_nao_falha_com_achado_sem_documento_e_entrega_o_achado():
    """C-01: a página do mapa do site que não abriu vira achado sem documento — antes, KeyError: 'url' derrubava a passagem."""
    enc = Encaminhamento.__new__(Encaminhamento)
    enc.diario = _D()
    a = Achado(id="m-mapa-1", motor="m", encontrado_em="2026-11-16", link_divulgacao="https://x.org/edital", link_oficial="https://x.org/edital",
               titulo="Edital", dados={"livro_id": "L1"}, documento=None)
    enc._entregar(a, "m")
    assert enc.diario.ev == ["achado.entregue"]
    from pathlib import Path
    m = Path("eldorado/motores/canal/motor.py").read_text(encoding="utf-8")
    assert "if p.link not in relevantes or p.link in nesta_rodada" in m   # a relevante além do limite não se perde


def test_o_posto_do_espiao_nao_mostra_missao_undefined():
    """C-19: o painel publica motor, título e desde — a página usa o título quando não há número da missão."""
    from pathlib import Path
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "Missão ${MA.n}/${MA.total} — ${esc(MA.missao)}</b>" not in p and 'esc(MA.missao||MA.titulo||"")' in p


def test_livro_devolvido_do_arquivo_com_prazo_aberto_usa_uma_regua_so():
    """C-02 (R46): a devolução do arquivo e a saída do Farol usam a mesma condição de prazo aberto (o livro ia e voltava)."""
    import inspect

    from eldorado.base.cartorio import auditoria
    from eldorado.base.cartorio.regua import PRAZO_ABERTO
    assert "inscricao_fim" in PRAZO_ABERTO and "situacao_prazo" in PRAZO_ABERTO
    assert "PRAZO_ABERTO" in inspect.getsource(auditoria.devolver_abertas_do_arquivo)
    assert "PRAZO_ABERTO" in inspect.getsource(auditoria.farol_so_com_prazo_aberto)
    assert '("certificacao", "farol")' in inspect.getsource(auditoria.devolver_abertas_do_arquivo)


def test_aviso_de_licitacao_nao_entra_e_o_ato_vizinho_nao_contamina():
    """C-03: o aviso de contratação direta ou de anulação é barrado; a dispensa vizinha fica fora do edital."""
    from eldorado.base.missao.regras_portao import portao_associacao
    from eldorado.motores.leitura.atos import recortar
    assert "aviso de licitação" in (portao_associacao({}, "AVISO DE CONTRATACAO DIRETA N 12/2026 SECRETARIA") or "")
    texto = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026\nSeleção de organizações da sociedade civil para projetos culturais no município.\n"
             "DISPENSA DE LICITAÇÃO Nº 44/2026\nRequisito: apresentar certidão negativa de débitos trabalhistas e atestado de capacidade.\n")
    atos = recortar(texto)
    assert len(atos) == 2 and "certidão negativa" not in atos[0]["texto"]


def test_os_que_fecham_em_7_dias_sao_contados_antes_do_corte():
    """C-18: a lista mostra 15; o total é o do banco (eram 45 e o relatório dizia 15)."""
    from eldorado.base.comandante.apresentar import _n7
    assert _n7({"fecham_em_7_dias": [1] * 15, "fecham_em_7_dias_total": 45}) == 45


def test_o_ocr_que_demora_nao_prende_a_leitura():
    """17/11/2026: o OCR passou a levar minutos por página e prendeu a Qualidade — agora tem tempo limite por página."""
    import time

    import pytest

    from eldorado.motores.leitura.ocr import OCR, OCRDemorou
    o = OCR.__new__(OCR)
    o._motor, o._tess, o.nome = (lambda img: time.sleep(5)), None, "lento"
    t0 = time.monotonic()
    with pytest.raises(OCRDemorou):
        o.texto(b"x", limite_s=0.5)
    assert time.monotonic() - t0 < 2


def test_o_prazo_da_api_vale_antes_do_texto():
    """17/11/2026: o Agente Cultural tinha 2 chamamentos de Goiás abertos e não entregava — o prazo vinha num campo da API."""
    from datetime import timedelta

    from eldorado.motores.canal.motor import _prazo_estruturado_vigente, hoje_local
    from eldorado.motores.descoberta.pistas import Pista
    futuro = (hoje_local() + timedelta(days=5)).isoformat()
    assert _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": {"date": futuro + " 23:59:00"}}))
    assert _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": futuro}))
    assert not _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": "2020-01-01"}))
    assert not _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api"))


def test_publicacao_do_wordpress_com_campo_nulo_e_lida_e_nao_derruba_a_fonte():
    """C-26: o título, a data ou o resumo nulos não quebram a leitura (TypeError em 27 de 31 leituras da Capta)."""
    import json

    from eldorado.motores.acesso.escada import Resposta
    from eldorado.motores.descoberta.estrutura_site import wordpress
    itens = [{"link": "https://x.org/a", "title": None, "date": None, "excerpt": None}, {"link": "https://x.org/b", "title": {"rendered": None}}]
    ps = wordpress(lambda u: Resposta(u, 200, json.dumps(itens).encode(), "application/json"), "https://x.org/wp-json/wp/v2/posts")
    assert [p.link for p in ps] == ["https://x.org/a", "https://x.org/b"]


def test_mapa_do_site_com_xml_imperfeito_e_aproveitado():
    """C-27: a marca mal fechada ou o lixo antes da declaração não derrubam a leitura; os endereços válidos ficam."""
    from eldorado.motores.descoberta.estrutura_site import ler_mapa
    xml = b'lixo antes <?xml version="1.0"?><urlset><url><loc>https://x.org/1</loc></url><url><loc>https://x.org/2</loc></urk></urlset>'
    tipo, itens = ler_mapa(xml)
    assert tipo == "urlset" and [i[0] for i in itens] == ["https://x.org/1", "https://x.org/2"]


def test_frase_generica_nao_certifica_os_anexos():
    """C-31: 136 certidões de Anexos com frase genérica («Edital completo disponível em…», «Documentos exigidos»)."""
    from eldorado.base.nucleo.ia import ANEXO_NOMEADO
    assert ANEXO_NOMEADO.search("conforme o Anexo II – Plano de Trabalho") and ANEXO_NOMEADO.search("ANEXO I - Formulário")
    assert not ANEXO_NOMEADO.search("Edital completo disponível em www.x.gov.br") and not ANEXO_NOMEADO.search("Documentos exigidos")


def test_o_ato_legislativo_vai_a_tabela_de_leis_e_so_a_oportunidade_vira_livro():
    """C-29 (R14): o projeto de lei acompanha-se na tabela de leis; o chamamento do Legislativo segue como livro."""
    from eldorado.base.cerebro.encaminhamento import ato_legislativo
    pl = Achado(id="c1", motor="alego-pl", encontrado_em="2026-11-17", link_divulgacao="https://al.go.leg.br/pl/1", link_oficial=None,
                titulo="PL nº 1.234/2026 — declara de utilidade pública a Associação X", dados={})
    lei = ato_legislativo(pl)
    assert lei["esfera"] == "estadual" and lei["numero"] == "PL 1.234/2026" and lei["id"] == "leg-c1"
    ch = Achado(id="c2", motor="alego-pl", encontrado_em="2026-11-17", link_divulgacao="https://al.go.leg.br/x", link_oficial=None,
                titulo="Edital de chamamento público para entidades — emendas impositivas 2027", dados={})
    assert ato_legislativo(ch) is None
    outro = Achado(id="c3", motor="site-capta", encontrado_em="2026-11-17", link_divulgacao="https://x", link_oficial=None, titulo="PL 1/2026", dados={})
    assert ato_legislativo(outro) is None


def test_a_rota_sem_resposta_em_24h_fica_fora_do_ar(tmp_path):
    """C-05: as 4 rotas mortas eram tentadas a cada 2 minutos (702 a 716 falhas em 3 dias); fora do ar, uma vez por turno."""
    import json
    import random
    from datetime import datetime, timezone

    from eldorado.motores.pilotos.espiao import FORA_DO_AR_MIN, Espiao
    e = Espiao(tmp_path / "c.db", lambda q: ([], []), lambda u: None, rnd=random.Random(1))
    agora = datetime.now(timezone.utc).isoformat()
    for _ in range(6):
        e.con.execute("INSERT INTO espiao_missao(em, familia, consulta, resultados, candidatos, achados, motivos, rotas, bloqueada) "
                      "VALUES (?, 'f', 'q', 0, 0, 0, '{}', ?, 0)", (agora, json.dumps(["ddgs-brave: falhou (Erro: x); descansa 2 min",
                                                                                     "searxng: 3 pista(s), 3 nova(s)"])))
    assert e.fora_do_ar("ddgs-brave") and not e.fora_do_ar("searxng") and FORA_DO_AR_MIN == 360


def test_dominio_pendente_na_lista_da_ponte_tenta_a_ponte_antes_do_local():
    """C-09: o atalho do domínio pendente pulava a ponte (64 domínios da lista entre os 187 pendentes)."""
    import inspect

    from eldorado.motores.acesso import escada
    assert escada.na_lista_da_ponte("https://www.tjgo.jus.br/x") is escada.na_lista_da_ponte("https://tjgo.jus.br/x")
    assert not escada.na_lista_da_ponte("https://exemplo-que-nao-esta-na-lista.org/")
    assert "ordem = [ponte, local] if ponte is not None and na_lista_da_ponte(url) else [local]" in inspect.getsource(escada)


def test_api_do_wordpress_sem_json_cai_para_a_pagina():
    """C-10: a resposta que não é a lista de publicações (HTML ou objeto de erro) faz a fonte ler a página do site."""
    import inspect
    import json

    import pytest

    from eldorado.motores.acesso.escada import Resposta
    from eldorado.motores.canal import motor
    from eldorado.motores.descoberta.estrutura_site import wordpress
    for corpo in (b"<html>erro</html>", json.dumps({"code": "rest_disabled"}).encode()):
        with pytest.raises(ValueError):
            wordpress(lambda u, c=corpo: Resposta(u, 200, c, "text/html"), "https://x.org/wp-json/wp/v2/posts")
    assert "a API do WordPress respondeu sem JSON" in inspect.getsource(motor)


def test_o_orgao_nunca_e_o_nome_do_proprio_motor():
    """C-11: nos agregadores o livro nascia com o site no lugar do financiador (13 livros)."""
    from eldorado.motores.canal.motor import orgao_real
    assert orgao_real("Bússola Social — Bússola Editais", "Bússola Social") is None
    assert orgao_real("Fundação Banco do Brasil", "Bússola Social") == "Fundação Banco do Brasil" and orgao_real(None, "x") is None


def test_o_degrau_maximo_conta_so_os_degraus_usados_nesta_execucao():
    """C-12: o degrau máximo vinha dos domínios semeados da memória (Wayback em 5.656 de 5.816 execuções)."""
    from eldorado.motores.acesso.escada import Escada

    class D:
        def __init__(self, nome):
            self.nome, self.pesado = nome, False
    e = Escada([D("1 · api"), D("7 · Wayback")], intervalo_padrao=0)
    e.aprendido["semeado.org"] = 1                       # a memória semeada não conta
    assert e.degrau_maximo() is None
    e._aprender("lido.org", 0)
    from eldorado.motores.acesso.escada import codigo
    assert e.degrau_maximo() == codigo(e.degraus[0])


def test_livro_com_uma_data_fica_sem_previsao():
    """C-08 (R57): com uma edição só, a previsão é «sem base» — sem data e sem alerta."""
    from datetime import date

    from eldorado.base.analise.previsao import SEM_BASE, prever
    assert prever([date(2026, 3, 10)], date(2026, 11, 17)) == SEM_BASE and SEM_BASE["alerta_em"] is None
    p = prever([date(2025, 3, 10), date(2026, 3, 12)], date(2026, 11, 17))
    assert p["proxima_abertura_prevista"] == "2027-03-11" and p["confianca"] > 0.3


def test_decisao_de_livro_arquivado_recebe_0_5():
    """C-06 (R57): a recompensa gravada é a do destino — Farol 1, arquivo 0,5; sem destino espera 14 dias."""
    from datetime import datetime, timedelta, timezone

    from eldorado.base.aprendizado.avaliar import pelo_destino
    agora = datetime.now(timezone.utc)
    em = (agora - timedelta(days=2)).isoformat()
    assert pelo_destino(["A"], {"A": 0.5}, em, agora)[0] == 0.5
    assert pelo_destino(["A", "F"], {"A": 0.5, "F": 1.0}, em, agora)[0] == 1.0
    assert pelo_destino([], {}, em, agora)[0] == 0.0
    assert pelo_destino(["X"], {}, em, agora) == (None, None)                                   # ainda sem destino: espera
    assert pelo_destino(["X"], {}, (agora - timedelta(days=20)).isoformat(), agora)[0] == 0.5


def test_nenhuma_missao_do_espiao_sem_objetivo(tmp_path):
    """C-07 (R57 «toda missão tem um objetivo com nome»): a missão pega o próximo objetivo da fila e o registra."""
    import json
    import random

    from eldorado.motores.pilotos.espiao import Espiao
    e = Espiao(tmp_path / "c.db", lambda q: ([], ["searxng: 0 pista(s), 0 nova(s)"]), lambda u: None, rnd=random.Random(1))
    e.con.executemany("INSERT INTO espiao_objetivo(id, tipo, alvo, prioridade, consultas) VALUES (?, ?, ?, ?, ?)",
                      [("OBJ-1", "financiador conhecido", "Secult-GO", 1, json.dumps(["site:goias.gov.br edital {ano}"])),
                       ("OBJ-2", "empresa do cadastro", "Empresa X", 2, json.dumps(['"Empresa X" edital {ano}']))])
    e.con.commit()
    m = e.missao()
    linha = e.con.execute("SELECT objetivo, consulta FROM espiao_missao ORDER BY id DESC LIMIT 1").fetchone()
    assert linha[0] == "OBJ-1" and "goias.gov.br" in linha[1] and m["familia"] == "rastro_de_patrocinio"
    assert e.con.execute("SELECT usos FROM espiao_objetivo WHERE id = 'OBJ-1'").fetchone()[0] == 1
    assert e.missao() and e.con.execute("SELECT objetivo FROM espiao_missao ORDER BY id DESC LIMIT 1").fetchone()[0] == "OBJ-2"


def _bib_mecanismo():
    import sqlite3
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE livro(id TEXT, titulo TEXT, situacao TEXT, estrela TEXT);"
                    "CREATE TABLE livro_dados(livro_id TEXT, situacao_prazo TEXT, inscricao_fim TEXT, tipo_livro TEXT, catalogo_ouro TEXT, codigo_ouro TEXT);"
                    "CREATE TABLE passaporte(livro_id TEXT, fase TEXT);"
                    "INSERT INTO livro VALUES ('M', 'Lei Rouanet — Lei nº 8.313/91', 'aguardando', 'ouro'), ('E', 'Edital PNAB 2026', 'aguardando', 'ouro');"
                    "INSERT INTO livro_dados VALUES ('M', 'aberta', NULL, NULL, '{\"tipo\": \"mecanismo\"}', 'BR-C99-0001'),"
                    "('E', 'aberta', NULL, NULL, '{\"tipo\": \"edital\"}', NULL);"
                    "INSERT INTO passaporte VALUES ('M', 'farol'), ('E', 'farol');")
    return b


def test_livro_de_mecanismo_com_link_de_lei_e_valido_e_nao_recebe_previsao_de_abertura():
    """C-24 (R60): o mecanismo ganha o tipo pela validação de ouro; sem previsão por edições; o Valor não é conflito."""
    import inspect

    from eldorado.base.analise import previsao
    from eldorado.base.cartorio import auditoria
    from eldorado.base.cartorio.mecanismo import classificar
    b = _bib_mecanismo()
    ev = _D()
    r = classificar(b, ev)
    assert r["mecanismos"] == 1 and r["novos"] == 1 and ev.ev == ["livro.tipo"]
    assert "_sem_mecanismo(con)" in inspect.getsource(previsao.calcular)
    assert "COALESCE(d.tipo_livro, '') <> 'mecanismo'" in inspect.getsource(previsao._sem_mecanismo)
    assert 'conflitos = [c for c in conflitos if c != "Valor"]' in inspect.getsource(auditoria.auditar)
    import json
    from pathlib import Path
    reg = json.loads(Path("config/missao/dispensas_por_regime.json").read_text(encoding="utf-8"))["regimes"]["mecanismo"]["itens"]
    assert reg["Prazo de inscrição"]["situacao"] == "nao_se_aplica" and "Valor" in reg


def test_mecanismo_nao_conta_como_aberta_sem_data_de_fim():
    """C-24 (R60): o mecanismo sai da conta de abertas e de «sem data de fim»; é contado à parte."""
    from eldorado.base.cartorio.regua import regua
    b = _bib_mecanismo()
    b.execute("UPDATE livro_dados SET tipo_livro = 'mecanismo' WHERE livro_id = 'M'")
    r = regua(b)
    assert r["abertas"] == 1 and r["mecanismos"] == 1


def test_o_codigo_de_ouro_resolve_o_territorio_indeterminado():
    """C-16: a abrangência verificada no edital (o código de ouro) vale quando o território está indeterminado."""
    from eldorado.base.cartorio.auditoria import abrangencia_do_codigo as a
    assert (a("GYN.GO-C01-AP-0001"), a("VAR.GO-D01-0002"), a("REC.PE-C04-0001"), a("GO-T01-AQ-0012"), a("SP-C01-0003"),
            a("BR-D01-AU-0003"), a("INT-X01-0002"), a(None)) == ("municipal_go", "municipal_go", "capital_outro_estado", "estadual_go",
                                                                  "estadual_outro_estado", "nacional", "internacional", None)


def test_o_mesmo_link_oficial_especifico_une_os_repetidos_e_o_generico_conta_como_ausente():
    """C-14 e C-15: o documento oficial é chave de união; a página inicial ou o portal não é origem."""
    from eldorado.base.cartorio.identidade import conflito, mesmo_link_especifico
    from eldorado.base.cartorio.origem import AUSENTE, classificar, link_especifico, link_generico
    assert link_generico("https://www.gov.br/cultura") and link_generico("https://fundacao.org/editais/")
    assert not link_generico("https://www.gov.br/saude/pt-br/pronon/edital-06-2026.pdf")
    assert not link_especifico("https://www.planalto.gov.br/ccivil_03/leis/l8313.htm")
    assert classificar("https://www.gov.br/cultura", "Ministério da Cultura")[0] == AUSENTE
    doc = "https://www.gov.br/saude/pt-br/pronon/edital-06-2026.pdf"
    a = {"oficial": doc, "titulo": "PRONON 06/2026", "fim": "2026-12-01"}
    b = {"oficial": doc.upper().replace("HTTPS://WWW.", "https://"), "titulo": "Edital PRONON 06/2026", "fim": "2026-12-01"}
    assert mesmo_link_especifico(a, b) and not conflito(a, b)
    assert not mesmo_link_especifico({"oficial": "https://www.gov.br/cultura"}, {"oficial": "https://www.gov.br/cultura"})


def test_livro_privado_com_financiador_gera_vinculo_e_livro_publico_nao_gera():
    """C-20 (decisão da titular de 16/11): empresa com oportunidade tem vínculo; o setor público fica sem vínculo."""
    import json
    import sqlite3

    from eldorado.base.cartorio.vinculo_empresa import vincular
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE livro(id TEXT, titulo TEXT, orgao TEXT, link_oficial TEXT, situacao TEXT);"
                    "CREATE TABLE livro_dados(livro_id TEXT, esfera TEXT, inscricao_inicio TEXT, inscricao_fim TEXT, catalogo_ouro TEXT);"
                    "CREATE TABLE empresa(cnpj TEXT, razao_social TEXT, nome_fantasia TEXT); CREATE TABLE vinculo_livro(cnpj TEXT, livro_id TEXT);"
                    "INSERT INTO empresa VALUES ('11.111.111/0001-11', 'Itaú Unibanco S.A.', 'Itaú');")
    b.executemany("INSERT INTO livro VALUES (?, ?, ?, NULL, 'aguardando')", [("P", "Edital Itaú Social", "Itaú"), ("G", "Edital PNAB", "Secult-GO"),
                                                                            ("N", "Edital Fundação X", None)])
    b.executemany("INSERT INTO livro_dados VALUES (?, ?, NULL, NULL, ?)", [("P", "privada", None), ("G", "estadual", None),
                                                                          ("N", "privada", json.dumps({"catalogo": {"financiador": "Fundação X"}}))])
    ev = _D()
    r = vincular(b, ev, "2026-11-17T00:00:00+00:00")
    assert r["vinculos"] == 2 and r["empresas_novas_pelo_nome"] == 1                   # Itaú pelo cadastro; Fundação X pelo nome
    assert ev.ev.count("vinculo_livro.registrado") == 2 and "G" not in str(ev.ev)


def test_o_andamento_das_leis_e_conferido():
    """C-21: as 27 leis tinham a data da importação; a revogação passa a ser lida na própria página."""
    import sqlite3
    from datetime import datetime, timezone

    from eldorado.base.cartorio.leis import acompanhar
    b = sqlite3.connect(":memory:")
    b.execute("CREATE TABLE lei(id TEXT, esfera TEXT, numero TEXT, ementa TEXT, situacao TEXT, link_oficial TEXT, atualizada_em TEXT)")
    b.executemany("INSERT INTO lei VALUES (?, 'federal', ?, 'x', 'vigente', ?, '2026-10-22')",
                  [("L1", "Lei 11.438/2006", "https://planalto.gov.br/L11438.htm"), ("L2", "Lei 8.313/1991", "https://planalto.gov.br/L8313.htm")])
    ev = _D()
    paginas = {"https://planalto.gov.br/L11438.htm": "LEI Nº 11.438 — Revogado pela Lei Complementar nº 222, de 2025",
               "https://planalto.gov.br/L8313.htm": "LEI Nº 8.313 — Restabelece princípios da Lei nº 7.505"}
    r = acompanhar(b, ev, paginas.get, datetime(2026, 11, 17, tzinfo=timezone.utc))
    assert r["conferidas"] == 2 and r["mudaram"] == ["Lei 11.438/2006: vigente → revogada"] and ev.ev == ["lei.registrada"] * 2
