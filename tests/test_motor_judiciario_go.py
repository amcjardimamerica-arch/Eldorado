"""Motor do Judiciário — CNJ e TJGO (02/10/2026): RSS paginado do TJGO, notícia e PDF do edital da comarca, busca do CNJ,
PNCP cruzado e habilitação prévia. Tudo sem rede: as respostas reproduzem o formato verificado no navegador do titular
(Joomla do TJGO, WordPress do CNJ) com os textos reais de Rio Verde e Goiânia."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from src import judiciario_go as J

ROOT = Path(__file__).resolve().parents[1]
RSS = "https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss"
N_RV = "https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs/17-tribunal/36713-1a-vara-de-execucao-penal-de-rio-verde-abre-edital-para"
N_GYN = "https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs/17-tribunal/35133-vara-de-execucao-penal-de-goiania-abre-edital-para-dest"


def item_rss(titulo, url, dia, desc="", cat="Tribunal"):
    return (f"<item><title>{titulo}</title><link>{url}</link><guid isPermaLink=\"true\">{url}</guid>"
            f"<description><![CDATA[<p>{desc}</p>]]></description><category>{cat}</category><pubDate>{dia}</pubDate></item>")


def rss(*itens):
    return ('<?xml version="1.0" encoding="utf-8"?><!-- generator="Joomla! - Open Source Content Management" -->'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Tribunal de Justiça do Estado de Goiás - '
            'Notícias</title>' + "".join(itens) + "</channel></rss>")


def pagina_tjgo(titulo, data, corpo, pdf=None):
    anexo = f'<p><a href="{pdf}">Edital nº 01/2026</a></p>' if pdf else ""
    return (f'<html><head><title>{titulo}</title><script>var x="Facebook";</script></head><body>'
            '<div class="menu"><a href="/files/2020/regimento.pdf">Regimento</a></div>'
            f'<div class="col-md-8"><div class="com-content-article item-page"> <meta itemprop="inLanguage" content="pt-BR"><h2>{titulo}</h2><dl class="article-info"><dd><time datetime="{data}T13:22:27-03:00">'
            f'Publicado: {data}</time></dd><dd>Acessos: 589</dd></dl><p>{corpo}</p>{anexo}'
            '<p>(Texto: Diretoria de Comunicação Social do TJGO)</p>'
            '<div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=x">Facebook</a></div></div>'
            '<footer><a href="/files/2024/carta-de-servicos.pdf">Carta de serviços</a></footer></body></html>')


RIO_VERDE = ("A 1ª Vara de Execução Penal da Comarca de Rio Verde publicou o Edital nº 01/2026 para seleção de projetos que poderão "
             "receber recursos provenientes de prestações pecuniárias aplicadas em processos criminais. Podem participar instituições "
             "públicas e privadas com finalidade social previamente cadastradas no Banco de Projetos Sociais da Corregedoria-Geral da "
             "Justiça de Goiás - CGJ/GO, disponível no site: https://corregedoria.tjgo.jus.br/basesocial, além de projetos voltados às "
             "atividades de caráter essencial nas áreas de segurança pública, educação e saúde, e desenvolvam as atividades no "
             "município de Rio Verde (GO) e respectivos distritos judiciários. Inscrições Os interessados podem se inscrever até 30 de "
             "setembro de 2026, por meio do e-mail, em formato PDF, ou presencialmente no Gabinete da 1ª Vara Criminal.")
GOIANIA = ("A 1ª Vara de Execução Penal da Comarca de Goiânia publicou, nesta segunda-feira (12), o Edital nº 01/2026, que abre processo "
           "de seleção de instituições públicas e privadas com finalidade social interessadas na destinação de recursos provenientes "
           "de prestações pecuniárias. O custeio dos projetos está amparado pelo artigo 257, §3º, do Código de Normas e Procedimentos "
           "Judiciais da Corregedoria-Geral da Justiça de Goiás. As instituições interessadas deverão apresentar requerimento de "
           "Habilitação até o dia 30 deste mês. Poderão participar da seleção entidades públicas ou privadas previamente credenciadas.")


class Web:
    """Rede de mentira: URL (ou prefixo terminado em *) → texto/bytes; registra o que foi pedido."""

    def __init__(self, rotas):
        self.rotas, self.pedidos = rotas, []

    def __call__(self, url, binario=False, max_bytes=0):
        self.pedidos.append(url)
        alvo = self.rotas.get(url)
        if alvo is None:
            alvo = next((v for k, v in self.rotas.items() if k.endswith("*") and url.startswith(k[:-1])), None)
        if alvo is None:
            raise RuntimeError("HTTP 404")
        if isinstance(alvo, Exception):
            raise alvo
        return alvo


class Leitura(unittest.TestCase):
    def test_rss_do_joomla_e_filtro_de_candidatas(self):
        x = rss(item_rss("1ª Vara de Execução Penal de Rio Verde abre edital para seleção de projetos com recursos de prestações pecuniárias",
                         N_RV, "Fri, 03 Jul 2026 13:22:27 -0300"),
                item_rss("Caso Daiane: justiça manda a júri popular síndico acusado", "https://www.tjgo.jus.br/x/37578-caso", "Thu, 01 Oct 2026 18:40:02 -0300"))
        itens = J.itens_do_rss(x)
        self.assertEqual([i["publicado"] for i in itens], ["2026-07-03", "2026-10-01"])
        self.assertEqual([J.candidata(i["titulo"], i["descricao"]) for i in itens], [True, False])
        self.assertTrue(J.candidata("Vepema lança edital para beneficiar entidades com recursos de pena"))
        self.assertTrue(J.candidata("Juiz abre edital para seleção de projetos sociais em Cocalzinho de Goiás"))
        self.assertFalse(J.candidata("Comarca de Hidrolândia suspenderá o expediente em 5 de outubro"))

    def test_artigo_pega_so_o_pdf_do_corpo_e_a_data(self):
        pdf = "/images/docs/ccs/03.07 - Edital 01-2026 - Destinacao Penas Pecuniarias-3.pdf"
        a = J.artigo(pagina_tjgo("1ª Vara de Execução Penal de Rio Verde abre edital", "2026-07-03", RIO_VERDE, pdf), N_RV, "",
                     ("www.tjgo.jus.br",))
        self.assertEqual(a["publicado"], "2026-07-03")
        self.assertEqual([p["url"] for p in a["pdfs"]],                                    # nem o do menu nem o do rodapé
                         ["https://www.tjgo.jus.br/images/docs/ccs/03.07%20-%20Edital%2001-2026%20-%20Destinacao%20Penas%20Pecuniarias-3.pdf"])
        self.assertTrue(a["banco_projetos"])
        self.assertIn("30 de setembro de 2026", a["texto"])
        self.assertNotIn("Facebook", a["texto"])

    def test_comarca_vara_numero_areas_e_restricao(self):
        casos = {"1ª Vara de Execução Penal de Rio Verde abre edital para seleção de projetos": "Rio Verde",
                 "Comarca de Piracanjuba publica edital para seleção de projetos sociais": "Piracanjuba",
                 "Juiz abre edital para seleção de projetos sociais em Cocalzinho de Goiás": "Cocalzinho de Goiás",
                 "Vepema lança edital para beneficiar entidades com recursos de pena": "Goiânia",
                 "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária": "Itaberaí",
                 "2º Juizado Especial Criminal de Aparecida de Goiânia seleciona projetos": "Aparecida de Goiânia"}
        for t, esperado in casos.items():
            self.assertEqual(J.comarca_de(t), esperado, t)
        e = J.extrair("1ª Vara de Execução Penal de Rio Verde abre edital", RIO_VERDE, "2026-07-03")
        self.assertEqual((e["comarca"], e["numero_edital"], e["fim"], e["restricao_territorial"]), ("Rio Verde", "01/2026", "2026-09-30", "Rio Verde"))
        self.assertEqual(e["areas_admitidas"], ["seguranca_publica", "educacao", "saude"])
        self.assertTrue(e["exige_banco_projetos"])
        self.assertEqual(e["vara"], "1ª Vara de Execução Penal")

    def test_prazo_relativo_deste_mes(self):
        """Goiânia, 12/01/2026: 'requerimento de Habilitação até o dia 30 deste mês' → 30/01/2026."""
        self.assertEqual(J.prazo(GOIANIA, "2026-01-12")[0], "2026-01-30")
        self.assertEqual(J.prazo("Os pedidos de habilitação serão recebidos até o dia 10 do próximo mês.", "2026-12-15")[0], "2027-01-10")
        self.assertIsNone(J.prazo("O projeto deve ser executado até o dia 30 deste mês de cada ano seguinte.", None)[0])


class Classificacao(unittest.TestCase):
    def c(self, titulo, texto, pub, hoje, fonte="A"):
        return J.classificar_item({"fonte": fonte, "titulo": titulo, "texto": texto, "publicado": pub}, hoje, {"janela_oportunidade_sem_prazo_dias": 20})

    def test_edital_aberto_encerrado_e_sem_prazo(self):
        t = "1ª Vara de Execução Penal de Rio Verde abre edital para seleção de projetos com recursos de prestações pecuniárias"
        r = self.c(t, RIO_VERDE, "2026-07-03", date(2026, 9, 10))
        self.assertEqual((r["veredito"], r["categoria"], r["fim"]), ("OPORTUNIDADE", "edital_destinacao", "2026-09-30"))
        self.assertIn("Banco de Projetos", r["motivos"][0])
        r = self.c(t, RIO_VERDE, "2026-07-03", date(2026, 10, 2))
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "edital_encerrado"))
        r = self.c("Comarca de Piracanjuba publica edital para seleção de projetos sociais com recursos de penas pecuniárias",
                   "A juíza publicou o edital de seleção de projetos sociais com recursos de prestação pecuniária.", "2026-09-25", date(2026, 10, 2))
        self.assertEqual((r["veredito"], r["fim"], r.get("prazo_a_confirmar")), ("OPORTUNIDADE", None, True))
        r = self.c("Comarca de Piracanjuba publica edital para seleção de projetos sociais com recursos de penas pecuniárias",
                   "A juíza publicou o edital de seleção de projetos sociais com recursos de prestação pecuniária.", "2026-06-01", date(2026, 10, 2))
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "edital_sem_prazo"))

    def test_resultado_regra_credenciamento_e_ruido(self):
        hoje = date(2026, 10, 2)
        r = self.c("Entidades de Anápolis recebem equipamentos comprados com recursos de prestações pecuniárias",
                   "A Vara de Execução Penal entregou equipamentos às entidades selecionadas no edital.", "2026-09-30", hoje)
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "resultado_ou_entrega"))
        r = self.c("Corregedoria edita provimento sobre a destinação das prestações pecuniárias",
                   "O provimento altera o Código de Normas, art. 257, sobre a destinação de valores.", "2026-09-30", hoje)
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "regra"))
        r = self.c("TJGO — Credenciamento de entidades sem fins lucrativos aptas à coleta de resíduos recicláveis",
                   "Credenciamento de entidades sem fins lucrativos aptas à coleta, triagem e destinação dos resíduos, até 22/07/2031.", "2026-07-22", hoje)
        self.assertEqual((r["veredito"], r["regime"]), ("OPORTUNIDADE", "credenciamento_osc_judiciario"))
        r = self.c("TJGO abre concurso público para servidores", "Edital do concurso público com 200 vagas.", "2026-09-30", hoje)
        self.assertEqual(r["veredito"], "RUIDO")
        r = self.c("Caso Daiane: justiça manda a júri popular síndico", "Sentença de pronúncia.", "2026-10-01", hoje)
        self.assertEqual(r["veredito"], "RUIDO")

    def test_cnj_de_outro_estado_e_ruido_e_de_goias_vale(self):
        hoje = date(2026, 10, 2)
        r = self.c("Juizado do Torcedor de Pernambuco financia projetos sociais com recursos de prestações pecuniárias",
                   "O juizado de Recife selecionou projetos.", "2026-09-20", hoje, fonte="C")
        self.assertEqual(r["veredito"], "RUIDO")
        r = self.c("Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária",
                   "A Comarca de Itaberaí publicou o Edital nº 02/2026; inscrições até 20 de outubro de 2026.", "2026-09-28", hoje, fonte="C")
        self.assertEqual((r["veredito"], r["comarca"], r["fim"]), ("OPORTUNIDADE", "Itaberaí", "2026-10-20"))

    def test_um_edital_em_duas_fontes_e_um_registro(self):
        hoje = date(2026, 10, 2)
        tj = {"fonte": "A", "titulo": "Comarca de Itaberaí abre edital para seleção de projetos sociais com prestação pecuniária",
              "texto": "A Comarca de Itaberaí publicou o Edital nº 02/2026; inscrições até 20 de outubro de 2026. CPF 123.456.789-00",
              "publicado": "2026-09-27", "url": "https://www.tjgo.jus.br/n/1", "pdfs": [{"url": "https://www.tjgo.jus.br/files/2026/09/ed.pdf"}]}
        cnj = {"fonte": "C", "titulo": "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária",
               "texto": "A Comarca de Itaberaí publicou o Edital nº 02/2026; inscrições até 20 de outubro de 2026.", "publicado": "2026-09-28",
               "url": "https://www.cnj.jus.br/edital-seleciona-projetos-de-itaberai/"}
        with mock.patch.object(J, "QUARENTENA", Path(tempfile.mkdtemp()) / "q.jsonl"):
            op, ac, cont = J.classificar_lote([cnj, tj], hoje)
        self.assertEqual((len(op), cont["duplicados"]), (1, 1))
        r = next(iter(op.values()))
        self.assertEqual((r["url"], r["confianca"], r["comarca"]), ("https://www.tjgo.jus.br/files/2026/09/ed.pdf", "primaria", "Itaberaí"))
        self.assertIn(cnj["url"], r["vista_tambem_em"])
        self.assertNotIn("123.456.789-00", r["evidencia"])                    # CPF não vai para o git


class Motor(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for nome, alvo in (("ESTADO", "estado/judiciario_go.json"), ("ESTADO_LOCAL", "estado/judiciario_go_local.json"),
                           ("QUARENTENA", "estado/quarentena.jsonl"), ("DB", "dados/oportunidades/oportunidades.jsonl")):
            p = mock.patch.object(J, nome, self.tmp / alvo); p.start(); self.addCleanup(p.stop)
        (self.tmp / "dados/oportunidades").mkdir(parents=True)
        (self.tmp / "dados/oportunidades/oportunidades.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in (
            {"id": "pncp1", "fonte_id": "pncp-api", "orgao": "GOIAS TRIBUNAL DE JUSTICA DO ESTADO DE GOIAS", "titulo": "Credenciamento de entidades sem fins lucrativos",
             "url": "https://pncp.gov.br/app/editais/02292266000180/2026/83", "fim": "2031-07-22"},
            {"id": "pncp2", "fonte_id": "pncp-api", "orgao": "PREFEITURA DE X", "titulo": "Chamamento", "url": "https://pncp.gov.br/app/editais/1/2026/1"},
        )) + "\n", encoding="utf-8")
        cfg = json.loads((ROOT / "config/judiciario_go.json").read_text(encoding="utf-8"))
        cfg["ritmo"] = {"pausa_segundos": 0, "espera_erro_segundos": 0}
        p = mock.patch.object(J, "_cfg", lambda: cfg); p.start(); self.addCleanup(p.stop)
        p = mock.patch.object(J, "_hoje_real", lambda: date(2026, 9, 10)); p.start(); self.addCleanup(p.stop)
        self.cfg = cfg

    def web(self):
        pdf = "https://www.tjgo.jus.br/images/docs/ccs/edital-rio-verde.pdf"
        p0 = rss(item_rss("1ª Vara de Execução Penal de Rio Verde abre edital para seleção de projetos com recursos de prestações pecuniárias",
                          N_RV, "Fri, 03 Jul 2026 13:22:27 -0300"),
                 item_rss("Caso Daiane: justiça manda a júri popular síndico", "https://www.tjgo.jus.br/n/37578-caso", "Wed, 09 Sep 2026 18:40:02 -0300"))
        velho = rss(item_rss("Vara de Execução Penal de Goiânia abre edital para destinação de recursos de prestações pecuniárias", N_GYN,
                             "Mon, 12 Jan 2026 15:50:01 -0300"))
        return Web({RSS: p0, RSS + "&limitstart=8": rss(), RSS + "&limitstart=*": velho,
                    N_RV: pagina_tjgo("1ª Vara de Execução Penal de Rio Verde abre edital", "2026-07-03", RIO_VERDE, pdf),
                    N_GYN: pagina_tjgo("Vara de Execução Penal de Goiânia abre edital", "2026-01-12", GOIANIA),
                    pdf: b"%PDF-1.4 sem texto",
                    "https://www.cnj.jus.br/?s=*": '<h2 class="t"><a href="https://www.cnj.jus.br/juizado-de-pernambuco-financia-projetos/">'
                                                    'Juizado do Torcedor de Pernambuco financia projetos sociais com recursos de prestações pecuniárias</a></h2>',
                    "https://www.cnj.jus.br/juizado-de-pernambuco-financia-projetos/": "<article><p>Recife: projetos sociais com prestação pecuniária.</p></article>"})

    def test_computador_le_o_tjgo_e_a_nuvem_entrega_a_base(self):
        web = self.web()
        with mock.patch.object(J, "_abrir", web), mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": "1"}, clear=False):
            r = J.ler_motor({"id": J.MOTOR_ID})
        self.assertEqual(r["diagnostico"]["rota"], "local")
        self.assertTrue(any(u.startswith(RSS) for u in web.pedidos))
        self.assertIn(N_RV, web.pedidos)
        self.assertNotIn("https://www.tjgo.jus.br/n/37578-caso", web.pedidos)            # notícia que não é candidata não é aberta
        self.assertFalse(any("cnj.jus.br" in u for u in web.pedidos))                      # o CNJ é da nuvem
        self.assertFalse(any("/basesocial/projects" in u for u in web.pedidos))            # lista com nomes e telefones: nunca
        local = json.loads((self.tmp / "estado/judiciario_go_local.json").read_text(encoding="utf-8"))
        rv = next(x for x in local["abertas_registros"] if x["comarca"] == "Rio Verde")
        self.assertEqual((rv["fim"], rv["numero_edital"], rv["url"]), ("2026-09-30", "01/2026", "https://www.tjgo.jus.br/images/docs/ccs/edital-rio-verde.pdf"))
        self.assertFalse((self.tmp / "estado/judiciario_go.json").exists())                 # o computador não grava o arquivo da nuvem
        self.assertTrue(local["rss"]["carga_concluida"])
        # a nuvem não toca no TJGO, lê o CNJ, cruza o PNCP e entrega à base o que o computador achou
        web2 = self.web()
        with mock.patch.object(J, "_abrir", web2), mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            r2 = J.ler_motor({"id": J.MOTOR_ID})
        self.assertEqual(r2["diagnostico"]["rota"], "nuvem")
        self.assertFalse(any("tjgo.jus.br" in u for u in web2.pedidos))
        self.assertTrue(any("cnj.jus.br/?s=" in u for u in web2.pedidos))
        self.assertIn("Rio Verde", [a["comarca"] for a in r2["achados"]])
        self.assertEqual(r2["diagnostico"]["vereditos"]["RUIDO"], 1)                       # Pernambuco
        est = json.loads((self.tmp / "estado/judiciario_go.json").read_text(encoding="utf-8"))
        self.assertEqual([x["id"] for x in est["pncp_cruzado"]], ["pncp1"])
        self.assertEqual(est["acompanhar"][0]["categoria"], "habilitacao_previa")
        self.assertNotIn("alerta_local", r2["diagnostico"])

    def test_rss_para_na_pagina_ja_vista_e_artigos_ficam_pendentes(self):
        web = self.web()
        self.cfg["fontes"]["A_noticias_tjgo"]["max_artigos_por_execucao"] = 1
        with mock.patch.object(J, "_abrir", web), mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": "1"}, clear=False):
            J.ler_motor({"id": J.MOTOR_ID})
            local = json.loads((self.tmp / "estado/judiciario_go_local.json").read_text(encoding="utf-8"))
            self.assertEqual(len(local["rss"]["pendentes"]), 1)                              # a 2ª notícia candidata espera a próxima vez
            web.pedidos.clear()
            J.ler_motor({"id": J.MOTOR_ID})
        self.assertEqual([u for u in web.pedidos if u.startswith(RSS)], [RSS])                # página 1 toda vista: para aí
        local = json.loads((self.tmp / "estado/judiciario_go_local.json").read_text(encoding="utf-8"))
        self.assertEqual(local["rss"]["pendentes"], [])
        self.assertTrue(any(a.get("comarca") == "Goiânia" for a in local["acompanhar"]))     # o edital de janeiro já venceu

    def test_cnj_recusado_na_nuvem_passa_ao_computador(self):
        from src.camara_goiania import Recusa
        web = self.web()
        web.rotas["https://www.cnj.jus.br/?s=*"] = Recusa("HTTP 403 — acesso negado")
        with mock.patch.object(J, "_abrir", web), mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            r = J.ler_motor({"id": J.MOTOR_ID})
        est = json.loads((self.tmp / "estado/judiciario_go.json").read_text(encoding="utf-8"))
        self.assertEqual(est["cnj"]["recusado_na_nuvem_em"], "2026-09-10")
        self.assertIn("alerta_local", r["diagnostico"])                                         # o computador ainda não rodou
        web2 = self.web()
        with mock.patch.object(J, "_abrir", web2), mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": "1"}, clear=False):
            J.ler_motor({"id": J.MOTOR_ID})
        self.assertTrue(any("cnj.jus.br/?s=" in u for u in web2.pedidos))

    def test_dia_passado_nao_e_relido(self):
        r = J.ler_motor({"id": J.MOTOR_ID}, date(2026, 9, 1))
        self.assertTrue(r["diagnostico"]["retroativo"])


class Integracao(unittest.TestCase):
    def test_sensor_unico_no_lugar_dos_dois_antigos(self):
        s = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        ids = [x["id"] for x in s["sensores_especiais"]]
        self.assertIn(J.MOTOR_ID, ids)
        self.assertNotIn("dje-tjgo", ids); self.assertNotIn("cnj-destinacoes", ids)
        sen = next(x for x in s["sensores_especiais"] if x["id"] == J.MOTOR_ID)
        from urllib.parse import urlsplit
        self.assertTrue({urlsplit(u).hostname for u in sen["urls"]} & set(s["exige_brasil"]["dominios"]))   # a coleta do computador o roda
        self.assertIn('if sensor.get("id") == "judiciario-cnj-tjgo"', (ROOT / "src/sensores.py").read_text(encoding="utf-8"))
        ag = json.loads((ROOT / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        for k in ("dje-tjgo", "cnj-destinacoes"):
            self.assertEqual((ag[k]["dias"], ag[k]["agregado_a"]), ("inativo", J.MOTOR_ID))
        # 02/10 (titular): o motor combinado foi SEPARADO em TJ-GO e CNJ — fica inativo, apontando para o TJ-GO
        self.assertEqual((ag[J.MOTOR_ID]["dias"], ag[J.MOTOR_ID]["agregado_a"]), ("inativo", "judiciario-tjgo"))
        self.assertEqual((ag["judiciario-tjgo"]["dias"], ag["judiciario-cnj"]["dias"]), ("todos", "todos"))
        tj = next(x for x in s["sensores_especiais"] if x["id"] == "judiciario-tjgo")
        self.assertTrue({urlsplit(u).hostname for u in tj["urls"]} & set(s["exige_brasil"]["dominios"]))   # o TJ-GO segue no computador
        fm = json.loads((ROOT / "config/finalidade_motores.json").read_text(encoding="utf-8"))["motores"]
        self.assertEqual(fm[J.MOTOR_ID]["finalidade"], "descoberta")
        cfg = json.loads((ROOT / "config/judiciario_go.json").read_text(encoding="utf-8"))
        self.assertFalse(cfg["fontes"]["F_djen"]["ativa"])
        self.assertIn("Resolução CNJ 558/2024", cfg["regra"])

    def test_sensores_ler_despacha(self):
        from src import sensores
        with mock.patch.object(J, "ler_motor", lambda s, d, l: {"sensor": "x", "ok": True}):
            self.assertTrue(sensores.ler({"id": J.MOTOR_ID, "urls": [], "tipo": "diario_justica", "nome": "x"})["ok"])


if __name__ == "__main__":
    unittest.main()


ITABERAI_HTML = ('<html><head><meta property="article:published_time" content="2020-07-21T14:27:00+00:00"></head><body>'
                 '<aside><time datetime="2026-10-02">2 out</time><time datetime="2026-09-21">21 set</time></aside>'
                 '<article class="post"><div class="entry-content"><p>Post publicado: 21 de julho de 2020</p>'
                 '<p>Entidades e instituições sociais de Itaberaí (GO) podem se inscrever, desde segunda-feira (20/7), para seleção dos '
                 'projetos que vão receber verbas provenientes de prestação pecuniária. O prazo termina no dia 18 de agosto. Podem '
                 'participar projetos de instituições com finalidade social nas áreas de segurança pública, educação e saúde. É '
                 'necessário que a atuação seja no município.</p></div></article><div class="share">x</div></body></html>')


class Motor11CNJ(unittest.TestCase):
    """Teste do motor 11 (CNJ) de 03/10/2026."""

    def test_data_do_meta_e_nao_da_barra_lateral(self):
        a = J.artigo(ITABERAI_HTML, "https://www.cnj.jus.br/edital-seleciona-projetos-de-itaberai/", "Edital seleciona projetos de Itaberaí (GO)")
        self.assertEqual(a["publicado"], "2020-07-21")
        sem_meta = ITABERAI_HTML.replace('<meta property="article:published_time" content="2020-07-21T14:27:00+00:00">', "")
        self.assertEqual(J.artigo(sem_meta, "https://www.cnj.jus.br/x/", "Edital")["publicado"], "2020-07-21")

    def test_noticia_de_2020_nao_e_oportunidade_e_restricao_e_detectada(self):
        a = J.artigo(ITABERAI_HTML, "https://www.cnj.jus.br/x/", "Edital seleciona projetos de Itaberaí (GO)")
        r = J.classificar_item({"fonte": "C", "titulo": "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária",
                                "texto": a["texto"], "publicado": a["publicado"]}, date(2026, 10, 3), {})
        self.assertEqual((r["veredito"], r["fim"]), ("ACOMPANHAR", "2020-08-18"))
        self.assertEqual(r["restricao_territorial"], "Itaberaí")

    def _rodar_c(self, paginas, vistos, lim=8):
        est = {"cnj": {"vistos": list(vistos), "datas_v2": "x"}}
        diag = {"fontes": {"C": {"falhas": [], "consultas": 0, "itens": 0}}}
        cfg = {"fontes": {"C_cnj_busca": {"busca": "https://www.cnj.jus.br/?s={termo}&orderby=date&order=DESC",
                                          "busca_pagina": "https://www.cnj.jus.br/page/{pagina}/?s={termo}&orderby=date&order=DESC",
                                          "termos": ["prestação pecuniária"], "max_paginas": 3, "max_artigos_por_execucao": lim}}}
        pedidas = []

        def get(url, cfg_, F, **kw):
            pedidas.append(url)
            if "/?s=" in url and "/page/" not in url:
                return paginas[0]
            if "/page/" in url:
                n = int(url.split("/page/")[1].split("/")[0])
                return paginas[n - 1] if n <= len(paginas) else ""
            return ITABERAI_HTML.replace("Itaberaí", "Goiânia")
        J._PARTE.update(id="judiciario-cnj", fontes="C")
        try:
            with mock.patch.object(J, "_get", side_effect=get):
                out = J.fonte_c(date(2026, 10, 3), cfg, diag, est, "nuvem")
        finally:
            J._PARTE.update(id=None, fontes="ABCDE")
        return out, diag, est, pedidas

    @staticmethod
    def _pagina(slugs):
        return "".join(f'<h2><a href="https://www.cnj.jus.br/{s}/">Edital de prestação pecuniária {s}</a></h2>' for s in slugs)

    def test_busca_por_data_ate_alcancar_o_ja_visto(self):
        p1, p2 = self._pagina(["nova-1", "nova-2"]), self._pagina(["nova-3", "velha-1"])
        out, diag, est, pedidas = self._rodar_c([p1, p2], ["https://www.cnj.jus.br/velha-1/"])
        self.assertTrue(all("orderby=date" in u for u in pedidas if "?s=" in u))
        self.assertEqual(len([u for u in pedidas if "?s=" in u]), 2)              # parou na página que tinha o já visto
        self.assertEqual(len(out), 3)
        self.assertNotIn("cortados", diag)
        self.assertEqual(est["cnj"]["ultima"], "2026-10-03")

    def test_corte_vira_leitura_parcial_e_volta(self):
        p = [self._pagina([f"n{i}-{k}" for k in range(4)]) for i in range(3)]      # 3 páginas sem alcançar o já visto
        out, diag, est, _ = self._rodar_c(p, ["https://www.cnj.jus.br/antiga/"], lim=5)
        self.assertEqual(len(out), 5)
        self.assertGreaterEqual(diag["cortados"], 1)                             # o maestro lê como PARCIAL
        self.assertNotIn("ultima", est["cnj"])                                   # a cadência não pula a próxima passagem

    def test_status_le_o_estado_de_cada_parte(self):
        from src import status_motores as S
        self.assertTrue(str(S.PROPRIOS["judiciario-cnj"]).endswith("estado/judiciario_cnj.json"))
        self.assertTrue(str(S.PROPRIOS["judiciario-tjgo"]).endswith("estado/judiciario_tjgo.json"))
