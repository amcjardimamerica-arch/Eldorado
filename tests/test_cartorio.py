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

    def test_robots_vai_ao_chrome(self):
        u = "https://www.goias.gov.br/edital.pdf"
        c = C.certificar({"id": "e3", "titulo": "x", "url": u}, ["Valor"], Rede({u: b""}, proibidos={u}))
        self.assertTrue(c["encaminhado"].startswith("Chrome"))


class TesteIntegracao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(C, k) for k in ("PASTA", "CERTIDOES", "LIVROS_OUT", "INTERCEPTADOR", "RELATORIO")}
        C.PASTA = T; C.CERTIDOES = T / "certidoes.json"; C.LIVROS_OUT = T / "livros.jsonl"
        C.INTERCEPTADOR = T / "para_int.json"; C.RELATORIO = T / "cartorio.json"; C._CACHE.clear()

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(C, k, v)
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
        self.assertEqual((r["fila_estrelas"], r["fila_livros"], r["certificadas"]), (1, 1, 2), "só entra quem tem item indisponível")
        self.assertEqual(C.item_checklist("est1", "Valor")["s"], "ok")
        self.assertEqual(C.link_oficial("est1"), pdf)
        cert = json.loads(C.CERTIDOES.read_text())["certidoes"]["estrela:est1"]
        self.assertEqual(cert["selo_depois"], "ouro", "a certidão transforma a estrela em ouro")
        linhas = [json.loads(l) for l in C.LIVROS_OUT.read_text().splitlines()]
        self.assertEqual(linhas[0]["livro"], "livro1"); self.assertIn("Valor", linhas[0]["doze"])
        sys.path.insert(0, str(ROOT / "scripts"))
        from importar_verificacao_livros import conferir
        self.assertEqual(conferir(linhas[0], {"livro1"}), [], "o importador aceita a linha do Cartório")
        rel = json.loads(C.RELATORIO.read_text())
        self.assertEqual(rel["resumo"]["certidoes"], 2); self.assertEqual(rel["resumo"]["eficiencia_itens"], 1.0)
        self.assertIn("itens", rel["certidoes"][0])
        self.assertEqual(C.run(10, 60, Rede({}), fluxo, catalogo)["certificadas"], 0, "não refaz o que não mudou")

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
        h = (ROOT / "docs/cartorio.html").read_text(encoding="utf-8")
        self.assertIn("dados/cartorio.json", h); self.assertIn("<details", h); self.assertNotIn("prefers-color-scheme: dark", h)


if __name__ == "__main__":
    unittest.main()
