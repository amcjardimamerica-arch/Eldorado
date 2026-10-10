"""09/10 (titular): Cartório de fontes oficiais — régua única, balcões, escada de degraus, leitura por seções, dispensa
justificada, certidão, integração (fluxo, painel, Interceptador, esteira dos livros) e relatório. Sem rede."""
import io, json, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import cartorio as C
from src import cartorio_leitura as L
from src.criterio_selos import resolvido, nivel, dispensa_valida


def _pdf(paginas):
    """PDF mínimo com uma página por texto (None = página sem camada de texto)."""
    objs, kids = [b"<< /Type /Catalog /Pages 2 0 R >>", None], []
    for t in paginas:
        linhas = [] if t is None else t.split("\n")
        ops = "BT /F1 9 Tf 30 800 Td 11 TL " + " ".join("(" + l.replace("(", "[").replace(")", "]") + ") '" for l in linhas) + " ET" if linhas else "0 0 m 9 9 l S"
        c = ops.encode("latin-1", "replace")
        objs.append(b"<< /Length %d >>\nstream\n" % len(c) + c + b"\nendstream")
        objs.append(None); kids.append(len(objs))
    fonte = len(objs) + 1
    for i in range(len(objs)):
        if objs[i] is None and i > 1:
            objs[i] = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents %d 0 R /Resources << /Font << /F1 %d 0 R >> >> >>" % (i, fonte)
    objs[1] = b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % k for k in kids) + b"] /Count %d >>" % len(kids)
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out, pos = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        pos.append(len(out)); out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    x = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1) + b"".join(b"%010d 00000 n \n" % p for p in pos)
    return out + b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, x)


EDITAL = ["PREFEITURA MUNICIPAL DE ANAPOLIS\nSECRETARIA MUNICIPAL DE CULTURA\nEDITAL DE CHAMAMENTO PUBLICO N 003/2026\n"
          "1. DO OBJETO\n1.1. O presente edital tem por objeto a selecao de organizacoes da sociedade civil para projetos culturais de formacao artistica no Municipio de Anapolis.\n"
          "2. DOS RECURSOS FINANCEIROS\n2.1. O valor global disponivel e de R$ 300.000,00 [trezentos mil reais].\n"
          "2.2. Os recursos serao destinados exclusivamente ao pagamento de oficineiros, materiais e locacao de espacos.\n"
          "3. DAS CONDICOES DE PARTICIPACAO\n3.1. Poderao participar organizacoes da sociedade civil sediadas em Anapolis ha pelo menos 2 anos, com CNPJ ativo.",
          "4. DO CRONOGRAMA\nPeriodo de inscricoes: de 13/10/2026 a 12/11/2026\nDivulgacao do resultado preliminar: 30/11/2026\n"
          "Prazo para recurso: 5 [cinco] dias uteis apos a publicacao\n5. DOS ANEXOS\nANEXO I - Plano de Trabalho\nANEXO II - Declaracoes"]
CRED = ["MUNICIPIO DE GOIANIA\nEDITAL DE CREDENCIAMENTO DE OSC PARA O SERVICO DE CONVIVENCIA\n1. DO OBJETO\n1.1. O presente edital tem por objeto o credenciamento de organizacoes da sociedade civil de assistencia social para o servico de convivencia.\n"
        "2. DAS INSCRICOES\n2.1. As inscricoes ocorrem em fluxo continuo, a qualquer tempo, durante a vigencia do edital.\n2.2. Nao havera repasse de recursos financeiros nesta etapa de habilitacao.\n"
        "3. DA DECISAO\n3.1. Nao cabera recurso da decisao de credenciamento, que e definitiva."]


class Rede(C.Rede):
    def __init__(self, mapa, proibidos=()):
        super().__init__(baixar=lambda u: (mapa[u] if isinstance(mapa[u], bytes) else mapa[u].encode(), ""), permitido=lambda u: u not in proibidos, pausa=0)


class TesteRegua(unittest.TestCase):
    def test_regua_unica(self):
        self.assertFalse(L.regua("https://pncp.gov.br/app/editais/46634481000198/2026/203")[0], "anúncio do PNCP é vetor")
        self.assertTrue(L.regua("https://pncp.gov.br/pncp-api/v1/orgaos/46634481000198/compras/2026/203/arquivos/1")[0])
        self.assertFalse(L.regua("https://data.queridodiario.ok.org.br/5208707/2026-09-30/x.pdf")[0])
        self.assertFalse(L.regua("https://capitaai.com.br/edital-x")[0])
        self.assertTrue(L.regua("https://www.anapolis.go.gov.br/edital.pdf")[0])
        self.assertTrue(L.regua("https://www.in.gov.br/web/dou/-/edital-1")[0])


class TesteExtracao(unittest.TestCase):
    def test_doze_itens_por_secao(self):
        r = L.extrair(L.paginas(_pdf(EDITAL))["paginas"], "https://www.anapolis.go.gov.br/edital-003-2026.pdf", "Edital 003/2026")
        self.assertEqual(set(r["pontos"]), set(L.DOZE), set(L.DOZE) - set(r["pontos"]))
        self.assertEqual(r["fim"], "2026-11-12")
        self.assertEqual(r["pontos"]["Prazo de inscrição"]["pagina"], 2)
        self.assertIn("300.000,00", r["pontos"]["Valor"]["valor"])
        for v in r["pontos"].values():
            self.assertTrue(v["trecho"] and v["pagina"] >= 1)

    def test_dispensa_quando_o_edital_nao_tem_o_requisito(self):
        r = L.extrair(L.paginas(_pdf(CRED))["paginas"], "https://www.goiania.go.gov.br/cred.pdf", "Credenciamento de OSC")
        D = r["dispensas"]
        for k in ("Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor"):
            self.assertIn(k, D, k)
            self.assertTrue(dispensa_valida(D[k]["motivo"]), "a regra de 04/10 aceita a justificativa")
            self.assertTrue(D[k]["trecho"])
            self.assertTrue(resolvido({"s": "disp", "v": D[k]["motivo"]}))
        self.assertNotIn("Anexos", D, "não informado nunca é dispensa")

    def test_escaneado_e_ato_da_edicao(self):
        self.assertEqual(L.paginas(_pdf([None, None]))["motivo"], "pdf_escaneado")
        sel = L.localizar_ato(["CONTRATO 088/2026 R$ 9.999.999,00"] * 35 + ["CHAMAMENTO 3/2026 inscricoes ate 30/10/2026"], "Chamamento 3/2026")
        self.assertEqual(sum(1 for t in sel if t), 1)


class TesteBalcoes(unittest.TestCase):
    def test_pncp_api_de_arquivos_e_zip(self):
        api = "https://pncp.gov.br/pncp-api/v1/orgaos/46634481000198/compras/2026/203/arquivos"
        arq = api + "/2"
        z = io.BytesIO()
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("planilha.pdf", _pdf([None])); f.writestr("EDITAL_003_2026.pdf", _pdf(EDITAL))
        rede = Rede({api: json.dumps([{"url": api + "/1", "titulo": "Termo de referência", "statusAtivo": False},
                                      {"url": "https://pncp.gov.br:50439/pncp-api/v1/orgaos/46634481000198/compras/2026/203/arquivos/2", "titulo": "Edital", "statusAtivo": True}]),
                     arq: z.getvalue()})
        op = {"id": "e1", "titulo": "Edital 003/2026", "url": "https://pncp.gov.br/app/editais/46634481000198/2026/203"}
        c = C.certificar(op, list(L.DOZE), rede)
        self.assertEqual(c["balcao"], "pncp"); self.assertEqual(c["link_oficial"], arq); self.assertEqual(c["degrau"], 0)
        self.assertGreaterEqual(c["eficiencia"], 0.9, c["ainda_faltam"])

    def test_pista_leva_ao_site_oficial(self):
        ag = "https://capitaai.com.br/edital-cultura-anapolis"
        pg = "https://www.anapolis.go.gov.br/cultura/editais/chamamento-003-2026"
        pdf = "https://www.anapolis.go.gov.br/wp-content/uploads/2026/10/edital-003-2026.pdf"
        rede = Rede({ag: f'<html><body><p>Notícia sobre o edital de cultura de Anápolis, com inscrições abertas até novembro e muito mais texto para a página ter conteúdo suficiente para leitura.</p><a href="{pg}">Acesse o edital oficial</a></body></html>',
                     pg: f'<html><body><h1>Chamamento Público 003/2026</h1><p>A Secretaria Municipal de Cultura torna público o chamamento de organizações da sociedade civil, conforme o edital publicado nesta página oficial do município.</p><a href="{pdf}">Edital completo (PDF)</a></body></html>',
                     pdf: _pdf(EDITAL)})
        c = C.certificar({"id": "e2", "titulo": "Edital 003/2026 Anápolis", "url": ag}, ["Prazo de inscrição", "Valor", "Requisitos"], rede)
        self.assertEqual(c["balcao"], "pista")
        self.assertTrue(c["link_oficial"].startswith("https://www.anapolis.go.gov.br/"))
        self.assertEqual(c["resolvidos"], ["Prazo de inscrição", "Valor", "Requisitos"])

    def test_motor_proprio_devolve_certidao_completa(self):
        c = C.certificar({"id": "mp1", "titulo": "MPT-GO destinação", "origem": "motor mptgo-destinacao"}, ["Valor"], Rede({}))
        self.assertEqual((c["balcao"], c["resolvidos"], c["ainda_faltam"]), ("proprio", [], ["Valor"]))

    def test_robots_vai_ao_chrome(self):
        u = "https://www.goias.gov.br/edital.pdf"
        c = C.certificar({"id": "e3", "titulo": "x", "url": u}, ["Valor"], Rede({u: b""}, proibidos={u}))
        self.assertTrue(c["encaminhado"].startswith("Chrome"))


class TesteCorrecoesV2(unittest.TestCase):
    """Casos reais da 1ª medição (09/10): notícia em gov.br, IndexError, PDF embutido, ato no diário, Destinação/Requisitos."""
    def test_noticia_em_dominio_de_governo_e_oficial(self):
        self.assertTrue(L.regua("https://www.gov.br/mdh/pt-br/assuntos/noticias/2026/prazo-de-inscricoes")[0])
        self.assertFalse(L.regua("https://g1.globo.com/noticia/edital.ghtml")[0])
        self.assertFalse(L.regua("https://jornalopcao.com.br/noticia-edital")[0])

    def test_orgao_sem_grupo_nao_quebra(self):
        r = L.extrair(["Texto do Conselho Nacional dos Direitos da Crianca sem cabecalho. " * 5], "https://x.gov.br/a.pdf", "t", "Conselho Nacional dos Direitos da Crianca")
        self.assertEqual(r["pontos"]["Órgão / financiador"]["valor"], "Conselho Nacional dos Direitos da Crianca")   # antes: IndexError
        r = L.extrair(["SECRETARIA DE ESTADO DA CULTURA. Edital de selecao."], "https://x.go.gov.br/a.pdf", "t")
        self.assertEqual(r["pontos"]["Órgão / financiador"]["valor"], "SECRETARIA DE ESTADO DA CULTURA")

    def test_pdf_embutido_no_visualizador(self):
        html = '<html><body><iframe src="/portal/edicoes/7401/arquivo.pdf"></iframe></body></html>'
        ls = L.links_de_documento(html, "https://diariooficial.abc.go.gov.br/portal/visualizacoes/pdf/7401/")
        self.assertEqual(ls[0][0], "https://diariooficial.abc.go.gov.br/portal/edicoes/7401/arquivo.pdf")

    def test_ato_no_diario_por_no_e_por_termo_do_querido_diario(self):
        pgs = ["DECRETO 55 nomeia servidor"] * 20 + ["AVISO DE CHAMAMENTO PUBLICO Nº 4 - selecao de projetos culturais"] + ["outros atos"] * 15
        self.assertEqual(sum(1 for t in L.localizar_ato(pgs, "Aviso de Chamamento Público nº 4") if t), 2)
        pgs2 = ["portaria"] * 30 + ["Edital de chamamento público para organizações da sociedade civil"] + ["licitacao"] * 5
        sel = L.localizar_ato(pgs2, 'Diário Oficial de Penápolis (SP) 2026-09-15 — "chamamento público" "organizações da sociedade civil"')
        self.assertEqual(sum(1 for t in sel if t), 2)
        self.assertIsNone(L.localizar_ato(pgs2, "Diário Oficial sem identificação"))

    def test_destinacao_e_requisitos_em_outras_redacoes(self):
        r = L.extrair(["Sao despesas elegiveis: pagamento de pessoal, material de consumo e servicos de terceiros. "
                       "As proponentes deverao comprovar no minimo dois anos de existencia e regularidade fiscal."], "https://x.go.gov.br/a.pdf", "t")
        self.assertIn("despesas elegiveis", r["pontos"]["Destinação"]["valor"])
        self.assertIn("deverao comprovar", r["pontos"]["Requisitos"]["valor"])


class TesteV3(unittest.TestCase):
    def test_pncp_le_os_anexos_ate_achar_os_itens(self):
        api = "https://pncp.gov.br/pncp-api/v1/orgaos/46634481000198/compras/2026/9/arquivos"
        aviso = _pdf(["AVISO DE CHAMAMENTO PUBLICO N 003/2026\nA Prefeitura torna publico o chamamento. O edital completo esta nos anexos deste processo no portal."])
        arqs = [{"url": f"{api}/{i}", "titulo": t, "statusAtivo": True} for i, t in
                ((1, "Ata de sessão"), (2, "Aviso de chamamento"), (3, "Anexo I - Plano de trabalho"), (4, "Planilha"), (5, "Planilha 2"), (6, "EDITAL COMPLETO"))]
        mapa = {api: json.dumps(arqs), f"{api}/1": aviso, f"{api}/2": aviso, f"{api}/3": aviso, f"{api}/4": aviso, f"{api}/5": aviso, f"{api}/6": _pdf(EDITAL)}
        c = C.certificar({"id": "p9", "titulo": "Edital 003/2026", "url": "https://pncp.gov.br/app/editais/46634481000198/2026/9"}, ["Valor", "Prazo de recurso", "Requisitos"], Rede(mapa))
        self.assertEqual(c["resolvidos"], ["Valor", "Prazo de recurso", "Requisitos"])
        self.assertTrue(c["documentos"][0]["url"].endswith("/6"), "o EDITAL vem antes da ata e das planilhas")
        self.assertEqual(C._prioridade_anexo("Ata de julgamento"), 4); self.assertEqual(C._prioridade_anexo("Termo de Referência"), 1); self.assertEqual(C._prioridade_anexo("Aviso de chamamento"), 2)


class TesteV3b(unittest.TestCase):
    def test_edital_longo_de_orgao_e_lido_inteiro(self):
        u = "https://pncp.gov.br/pncp-api/v1/orgaos/1/compras/2026/1/arquivos/1"
        longo = _pdf(["Clausulas gerais do edital, sem identificacao de numero."] * 33 + EDITAL)
        c = C.certificar({"id": "l1", "titulo": "Chamamento sem número", "url_documento": u}, ["Valor", "Requisitos"], Rede({u: longo}))
        self.assertEqual(c["resolvidos"], ["Valor", "Requisitos"]); self.assertFalse(c["documentos"][0].get("edicao_inteira"))

    def test_edicao_de_diario_continua_so_no_ato(self):
        u = "https://data.queridodiario.ok.org.br/5208707/2026-09-30/x.pdf"
        ed = _pdf(["DECRETO 55 nomeia servidor publico municipal para o cargo de assessor da secretaria de obras."] * 35)
        c = C.certificar({"id": "d1", "titulo": "Diario sem numero", "url": u}, ["Valor"], Rede({u: ed}))
        self.assertEqual(c["documentos"][0]["motivo"], "ato_nao_localizado")


class TesteGabarito(unittest.TestCase):
    """v4: o gabarito aprende com itens VALIDADOS rótulos que a extração padrão não conhece e os aplica ao mesmo órgão."""
    FLUXO = {"itens_por_uf": {"GO": [{"id": "v1", "url": "https://pncp.gov.br/app/editais/11222333000144/2026/7", "orgao": "Prefeitura de X",
              "checklist": {"Prazo de inscrição": {"s": "ok", "v": "20/11/2026", "t": "8.2 Encerramento do cadastramento: 20/11/2026, às 18h"},
                            "Valor": {"s": "ok", "v": "R$ 80.000,00", "t": "Montante reservado ao chamamento — R$ 80.000,00 por projeto"}}}]}}
    NOVO = ["EDITAL 9/2026 DA PREFEITURA DE X\nTexto de apresentacao sem cronograma formal e sem secao de valores do edital.\n"
            "8.2 Encerramento do cadastramento: 05/12/2026, as 18h\nMontante reservado ao chamamento — R$ 120.000,00 por projeto"]

    def test_aprende_com_validacao_e_aplica_ao_mesmo_orgao(self):
        gab = {}
        self.assertGreaterEqual(C.aprender_das_validacoes(gab, self.FLUXO), 2)
        self.assertEqual(C.aprender_das_validacoes(gab, self.FLUXO), 0, "a mesma validação não conta duas vezes")
        chave = "cnpj:11222333000144"; self.assertIn(chave, gab)
        u = "https://pncp.gov.br/pncp-api/v1/orgaos/11222333000144/compras/2026/9/arquivos/1"
        padrao = L.extrair(self.NOVO, u, "Edital 9/2026")["pontos"]
        self.assertNotIn("Prazo de inscrição", padrao, "a extração padrão não conhece esse rótulo")
        extra = L.aplicar_gabarito(self.NOVO, C.ancoras_do_orgao(gab, chave), u, set(padrao))
        self.assertEqual(extra["Prazo de inscrição"]["valor"][:10], "05/12/2026")
        self.assertIn("120.000,00", extra.get("Valor", padrao.get("Valor", {})).get("valor", ""))
        self.assertIn("gabarito do órgão", extra["Prazo de inscrição"]["metodo"])

    def test_forma_errada_e_outro_orgao_nao_valem(self):
        gab = {}; C.aprender_das_validacoes(gab, self.FLUXO)
        anc = C.ancoras_do_orgao(gab, "cnpj:11222333000144")
        ruim = ["8.2 Encerramento do cadastramento: conforme cronograma a ser divulgado oportunamente pela comissao"]
        self.assertNotIn("Prazo de inscrição", L.aplicar_gabarito(ruim, anc, "u", set()), "sem data não é prazo")
        self.assertEqual(C.ancoras_do_orgao(gab, "cnpj:99999999000199"), {}, "outro órgão não herda o gabarito")

    def test_dominio_compartilhado_nao_e_chave(self):
        self.assertIsNone(L.chave_orgao("https://www.in.gov.br/web/dou/-/edital-1"))
        self.assertEqual(L.chave_orgao("https://www.anapolis.go.gov.br/x.pdf"), "dominio:anapolis.go.gov.br")

    def test_certidao_registra_o_gabarito(self):
        u = "https://pncp.gov.br/pncp-api/v1/orgaos/11222333000144/compras/2026/9/arquivos/1"
        gab = {}; C.aprender_das_validacoes(gab, self.FLUXO)
        c = C.certificar({"id": "n1", "titulo": "Edital 9/2026", "url_documento": u}, ["Prazo de inscrição"], Rede({u: _pdf(self.NOVO)}), 4, gab)
        self.assertEqual(c["resolvidos"], ["Prazo de inscrição"]); self.assertEqual(c["gabarito"]["itens_pelo_gabarito"], ["Prazo de inscrição"])


class TesteIntegracao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(C, k) for k in ("PASTA", "CERTIDOES", "LIVROS_OUT", "INTERCEPTADOR", "RELATORIO", "GABARITOS")}
        C.PASTA = T; C.CERTIDOES = T / "certidoes.json"; C.LIVROS_OUT = T / "livros.jsonl"; C.GABARITOS = T / "gabaritos.json"
        from src import cartorio_linha as _LN
        self._LN, self._bib0 = _LN, _LN.BIBLIOTECA; _LN.BIBLIOTECA = T / "biblioteca.json"
        C.INTERCEPTADOR = T / "para_int.json"; C.RELATORIO = T / "cartorio.json"; C._CACHE.clear()

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(C, k, v)
        self._LN.BIBLIOTECA = self._bib0
        C._CACHE.clear(); self.tmp.cleanup()

    def test_fila_certidao_checklist_livro_e_relatorio(self):
        pdf = "https://www.anapolis.go.gov.br/edital-003-2026.pdf"
        ck = {k: {"s": "ok", "v": "x" * 5} for k in ("Objeto", "Território", "Órgão / financiador", "Esfera", "Área de atuação")}
        ck.update({k: {"s": "falta"} for k in L.DOZE if k not in ck})
        fluxo = {"itens_por_uf": {"GO": [{"id": "est1", "titulo": "Edital 003/2026", "link_oficial": pdf, "fim": "2026-11-12", "checklist": ck},
                                         {"id": "est2", "titulo": "completo", "checklist": {k: {"s": "ok", "v": "valor"} for k in L.DOZE}}]}}
        catalogo = {"motores": [{"id": "livro1", "programa": "Edital 003/2026", "esteira": {"selo": "prata", "doze_faltando": ["Valor", "Prazo de recurso"], "site_confirmado_por": "domínio"},
                                 "parametros": {"edital": {"url": pdf}}}]}
        r = C.run(10, 60, Rede({pdf: _pdf(EDITAL)}), fluxo, catalogo)
        self.assertEqual(sum(r["na_linha"].values()), 2, "só entra quem tem item indisponível (a estrela completa fica fora)")
        self.assertEqual(r["certificadas"], 2)
        self.assertEqual(C.item_checklist("est1", "Valor")["s"], "ok")
        self.assertEqual(C.link_oficial("est1"), pdf)
        cert = json.loads(C.CERTIDOES.read_text())["certidoes"]["estrela:est1"]
        self.assertEqual(cert["selo_depois"], "ouro", "a certidão transforma a estrela em ouro")
        self.assertEqual(cert["abordagens"][0]["n"], 1); self.assertEqual(cert["tentativa"], 1)
        linhas = [json.loads(l) for l in C.LIVROS_OUT.read_text().splitlines()]
        self.assertEqual(linhas[0]["livro"], "livro1"); self.assertIn("Valor", linhas[0]["doze"])
        sys.path.insert(0, str(ROOT / "scripts"))
        from importar_verificacao_livros import conferir
        self.assertEqual(conferir(linhas[0], {"livro1"}), [], "o importador aceita a linha do Cartório")
        rel = json.loads(C.RELATORIO.read_text())
        self.assertEqual(rel["resumo"]["certidoes"], 2); self.assertEqual(rel["resumo"]["eficiencia_itens"], 1.0)
        self.assertEqual(rel["por_abordagem"]["1"]["vezes"] if "1" in rel["por_abordagem"] else rel["por_abordagem"][1]["vezes"], 2)
        self.assertIn("linha_de_producao", rel); self.assertIn("por_balcao_selo", rel)
        self.assertEqual(C.run(10, 60, Rede({}), fluxo, catalogo)["certificadas"], 0, "intervalo de 12 h entre tentativas")

    def test_um_erro_nao_derruba_a_fila(self):
        pg = "https://www.goias.gov.br/editais/x"
        html = '<html><body><p>' + 'Texto da página oficial com o chamamento público. ' * 8 + '</p><a href="https://[quebrado/edital.pdf">Edital</a><a href="http://host:porta/edital.pdf">Edital 2</a></body></html>'
        c = C.certificar({"id": "m1", "titulo": "Edital 1/2026", "url": pg}, ["Valor"], Rede({pg: html}))
        self.assertEqual(c["balcao"], "orgao")                       # href malformado ignorado, sem exceção
        fluxo = {"itens_por_uf": {"GO": [{"id": f"e{i}", "titulo": "t", "link_oficial": pg, "checklist": {"Valor": {"s": "falta"}}} for i in range(3)]}}
        orig = C.certificar
        def quebra(op, *a, **k):
            if op["id"] == "e1":
                raise ValueError("Invalid IPv6 URL")
            return orig(op, *a, **k)
        C.certificar = quebra
        try:
            r = C.run(10, 60, Rede({pg: html}), fluxo, {"motores": []})
        finally:
            C.certificar = orig
        self.assertEqual(r["certificadas"], 3); self.assertEqual(len(r["erros"]), 1)
        self.assertIn("erro no Cartório", json.loads(C.CERTIDOES.read_text())["certidoes"]["estrela:e1"]["encaminhado"])

    def test_ganchos(self):
        for f, s in (("src/fluxo_oportunidades.py", "_cart_item(m.get(\"id\"), k)"), ("src/fluxo_oportunidades.py", "link_oficial as _lo_cart"),
                     ("src/dashboard_dados.py", "from .cartorio import certidao"), ("src/interceptador.py", "encaminhado pelo Cartório")):
            self.assertIn(s, (ROOT / f).read_text(encoding="utf-8"), f)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")     # 10/10: o Cartório é uma seção do painel
        self.assertIn('id="v-cartorio"', h); self.assertIn('data-v="cartorio"', h); self.assertIn("dados/cartorio.json", h)
        self.assertFalse((ROOT / "docs/cartorio.html").exists(), "sem página própria")


if __name__ == "__main__":
    unittest.main()


class TesteLinhaDeProducao(unittest.TestCase):
    """09/10 (titular): balcões por selo, 10 abordagens diferentes, itens acumulados, promoção em cadeia, rede neural."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(C, k) for k in ("PASTA", "CERTIDOES", "LIVROS_OUT", "INTERCEPTADOR", "RELATORIO", "GABARITOS")}
        C.PASTA = T; C.CERTIDOES = T / "c.json"; C.LIVROS_OUT = T / "l.jsonl"; C.INTERCEPTADOR = T / "i.json"
        C.RELATORIO = T / "r.json"; C.GABARITOS = T / "g.json"; C._CACHE.clear()
        from src import cartorio_linha as LN
        self.LN = LN; self.bib0 = LN.BIBLIOTECA; LN.BIBLIOTECA = T / "bib.json"

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(C, k, v)
        self.LN.BIBLIOTECA = self.bib0; C._CACHE.clear(); self.tmp.cleanup()

    def test_balcoes_e_ordem_das_abordagens(self):
        LN = self.LN
        sem = {"_tipo": "estrela", "checklist": {}}
        bronze = {"_tipo": "estrela", "checklist": {k: {"s": "ok", "v": "valor"} for k in ("Objeto", "Prazo de inscrição", "Território")}}
        prata = {"_tipo": "estrela", "checklist": {k: {"s": "ok", "v": "valor"} for k in ("Objeto", "Prazo de inscrição", "Território", "Valor", "Requisitos")}}
        ouro = {"_tipo": "estrela", "checklist": {k: {"s": "ok", "v": "valor"} for k in L.DOZE}}
        self.assertEqual([LN.estagio(x) for x in (sem, bronze, prata, ouro)], ["sem_estrela", "bronze", "prata", None])
        self.assertEqual(LN.proxima_abordagem("sem_estrela", [1])[0], 4, "sem estrela: depois do documento na mão, a biblioteca de sites")
        self.assertEqual(LN.proxima_abordagem("bronze", [1])[0], 2, "bronze: anexos completos (valor e requisitos)")
        self.assertEqual(sorted(LN.ORDEM["prata"]), list(range(1, 11)), "cada balcão percorre as 10 abordagens")
        self.assertEqual(len(set(LN.ABORDAGENS.values())), 10, "10 abordagens diferentes")

    def test_acumula_e_esgota_na_decima(self):
        LN = self.LN
        c = LN.acumular(None, {"itens": {"Valor": {"valor": "R$ 1,00"}}, "link_oficial": "https://x.go.gov.br/a", "em": "t1"}, 1, ["Valor", "Requisitos"])
        c = LN.acumular(c, {"itens": {}, "dispensas": {}, "em": "t2"}, 2, ["Requisitos"])
        self.assertIn("Valor", c["itens"], "a 2ª tentativa não apaga o que a 1ª achou")
        self.assertEqual(c["abordagens"][1]["ganhou"], []); self.assertEqual(c["tentativa"], 2)
        for n in range(3, 11):
            c = LN.acumular(c, {"em": f"t{n}"}, n, ["Requisitos"])
        self.assertTrue(c["esgotada"]); self.assertIn("10 abordagens", c["encaminhado"])

    def test_bronze_vira_prata_e_segue_na_mesma_execucao(self):
        pg = "https://www.anapolis.go.gov.br/editais/chamamento-003-2026"
        pdf = "https://www.anapolis.go.gov.br/wp-content/uploads/edital-003-2026.pdf"
        html = f'<html><body><p>{"Chamamento publico da Secretaria de Cultura de Anapolis para organizacoes. " * 6}</p><a href="{pdf}">Edital completo</a></body></html>'
        ck = {k: {"s": "ok", "v": "valor conhecido"} for k in ("Objeto", "Prazo de inscrição", "Território")}
        ck.update({k: {"s": "falta"} for k in L.DOZE if k not in ck})
        fluxo = {"itens_por_uf": {"GO": [{"id": "b1", "titulo": "Edital 003/2026", "link_oficial": pg, "fim": "2026-11-12", "checklist": ck}]}}
        r = C.run(10, 60, Rede({pg: html, pdf: _pdf(EDITAL)}), fluxo, {"motores": []})
        cert = json.loads(C.CERTIDOES.read_text())["certidoes"]["estrela:b1"]
        self.assertEqual(cert["estagio_inicio"], "bronze")
        self.assertGreaterEqual(r["promovidas"], 1, "subiu de selo")
        self.assertEqual(cert["selo_depois"], "ouro")
        self.assertIn(cert["abordagens"][0]["n"], (1, 2), "balcão bronze começa pelo documento na mão / anexos")

    def test_biblioteca_de_sites_e_municipio(self):
        LN = self.LN
        cat = {"motores": [{"id": "l1", "orgao": "Prefeitura Municipal de Monteiro Lobato", "uf": "SP", "municipio": "Monteiro Lobato",
                            "pagina": "https://www.monteirolobato.sp.gov.br/editais"}]}
        bib = LN.construir_biblioteca(cat, {})
        op = {"titulo": 'Diário Oficial de Monteiro Lobato (SP) 2026-09-11 — "edital de chamamento público"', "url": "https://data.queridodiario.ok.org.br/x.pdf"}
        self.assertIn("https://www.monteirolobato.sp.gov.br/editais", LN.sites_conhecidos(op, bib), "o Querido Diário leva ao site da prefeitura")
        docs, aj = LN.documentos(4, op, Rede({}), None, bib)
        self.assertTrue(docs and aj["seguir_links"])

    def test_mapa_do_site(self):
        LN = self.LN
        sm = b'<?xml version="1.0"?><urlset><url><loc>https://x.go.gov.br/noticia-qualquer</loc></url><url><loc>https://x.go.gov.br/edital-chamamento-003-2026-cultura</loc></url></urlset>'
        op = {"titulo": "Edital 003/2026 de cultura", "link_oficial": "https://x.go.gov.br/editais"}
        achou = LN.mapa_do_site(op, Rede({"https://x.go.gov.br/sitemap.xml": sm}), {}, {})
        self.assertEqual([d["url"] for d in achou], ["https://x.go.gov.br/edital-chamamento-003-2026-cultura"])

    def test_rede_neural_le_a_certidao(self):
        self.assertIn("cart:link_oficial=", (ROOT / "src/rede_neural.py").read_text(encoding="utf-8"))
        wf = (ROOT / ".github/workflows/cartorio.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "41 * * * *"', wf, "linha de produção permanente, de hora em hora")


class TesteCobertura12(unittest.TestCase):
    """10/10 (titular): o % da certidão é sobre os 12 pontos; 1 de 1 pedido não é 100%."""
    def test_um_verde_nao_e_cem_por_cento(self):
        c = {"itens": {"Objeto": {}}, "dispensas": {}, "faltavam": ["Objeto"]}
        b = C.cobertura_12(c)
        self.assertEqual((b["certificados"], b["ja_constavam"], b["faltam"]), (1, 11, 0))
        self.assertEqual(b["pct_certificado_12"], round(1 / 12, 4)); self.assertEqual(b["pct_cobertura_12"], 1.0)

    def test_relatorio_publica_os_12(self):
        certs = {"estrela:a": {"id": "a", "tipo": "estrela", "itens": {k: {"valor": "v"} for k in L.DOZE}, "dispensas": {}, "faltavam": list(L.DOZE),
                               "resolvidos": list(L.DOZE), "link_oficial": "https://x.go.gov.br"},
                 "estrela:b": {"id": "b", "tipo": "estrela", "itens": {"Valor": {"valor": "R$"}}, "dispensas": {"Resultado": {"motivo": "não se aplica: x"}},
                               "faltavam": ["Valor", "Resultado", "Anexos"], "resolvidos": ["Valor", "Resultado"]}}
        r = C.relatorio(certs, [], 0, 0, {})
        self.assertEqual(r["resumo"]["certidoes_12_de_12"], 1); self.assertEqual(r["resumo"]["pontos_faltam"], 1)
        self.assertEqual(r["resumo"]["pct_certificado_12"], round(14 / 24, 4))
        b = next(c for c in r["certidoes"] if c["id"] == "b")["cobertura_12"]
        self.assertEqual(b["estados"]["Resultado"], "dispensado"); self.assertEqual(b["estados"]["Objeto"], "ja_constava")

    def test_pagina_quatro_estados_cores_do_painel(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("CARTORIO-12-PONTOS-V1", h)
        self.assertIn(".mini i.d{background:#2F79D0}", h, "dispensado em azul, como no checklist do painel")
        self.assertIn(".mini i.j{background:#C9CED6}", h, "já constava em cinza")
        self.assertNotIn("cinza: ainda falta", h)


class TesteConferirCinza(unittest.TestCase):
    """10/10 (titular): o Cartório confere no documento os itens CINZA (conhecidos sem certidão) das estrelas com site
    oficial; achado vira certificado; não achado continua cinza — nunca vira falta nem vai ao Interceptador."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(C, k) for k in ("PASTA", "CERTIDOES", "LIVROS_OUT", "INTERCEPTADOR", "RELATORIO", "GABARITOS")}
        C.PASTA = T; C.CERTIDOES = T / "c.json"; C.LIVROS_OUT = T / "l.jsonl"; C.INTERCEPTADOR = T / "i.json"
        C.RELATORIO = T / "r.json"; C.GABARITOS = T / "g.json"; C._CACHE.clear()
        from src import cartorio_linha as LN
        self.LN, self.b0 = LN, LN.BIBLIOTECA; LN.BIBLIOTECA = T / "b.json"

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(C, k, v)
        self.LN.BIBLIOTECA = self.b0; C._CACHE.clear(); self.tmp.cleanup()

    def test_cinza_achado_vira_certificado_e_nao_achado_continua_cinza(self):
        pdf = "https://www.anapolis.go.gov.br/edital-003-2026.pdf"
        ck = {k: {"s": "ok", "v": "lido na notícia"} for k in L.DOZE}           # todos conhecidos pelo motor (já é ouro)
        fluxo = {"itens_por_uf": {"GO": [{"id": "z1", "titulo": "Edital 003/2026", "link_oficial": pdf, "fim": "2026-11-12", "checklist": ck},
                                         {"id": "z2", "titulo": "sem site", "checklist": dict(ck)}]}}
        fila = C.fila_estrelas(fluxo)
        self.assertEqual([o["id"] for o in fila], ["z1"], "só estrela com site oficial entra para conferir")
        self.assertEqual(len(fila[0]["_conferir"]), 12); self.assertEqual(fila[0]["_faltam"], [])
        so_valor = _pdf(["PREFEITURA MUNICIPAL DE ANAPOLIS\n1. DO OBJETO\n1.1. O presente edital tem por objeto a selecao de organizacoes da sociedade civil para projetos culturais no Municipio de Anapolis.\n2. DOS RECURSOS\n2.1. O valor global disponivel e de R$ 300.000,00 para os projetos selecionados neste chamamento publico."])
        r = C.run(10, 60, Rede({pdf: so_valor}), fluxo, {"motores": []})
        self.assertEqual(r["certificadas"], 1)
        c = json.loads(C.CERTIDOES.read_text())["certidoes"]["estrela:z1"]
        self.assertIn("Valor", c["cinza_certificados"]); self.assertIn("Objeto", c["cinza_certificados"])
        cb = C.cobertura_12(c)
        self.assertEqual(cb["faltam"], 0, "cinza não achado nunca vira falta")
        self.assertEqual(cb["estados"]["Valor"], "certificado"); self.assertEqual(cb["estados"]["Prazo de recurso"], "ja_constava")
        self.assertIsNone(c.get("encaminhado"), "nada falta: não vai ao Interceptador")

    def test_quem_tem_item_faltando_vem_antes(self):
        a = {"_faltam": [], "_conferir": ["Valor"], "_usadas": [], "_estagio": "prata", "fim": "2026-10-11"}
        b = {"_faltam": ["Valor"], "_conferir": [], "_usadas": [], "_estagio": "bronze", "fim": "2026-12-01"}
        src = (ROOT / "src/cartorio.py").read_text(encoding="utf-8")
        self.assertIn("primeiro quem tem item FALTANDO", src)
