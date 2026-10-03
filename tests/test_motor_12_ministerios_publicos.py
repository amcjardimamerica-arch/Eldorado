"""02/10/2026: motor 12 — Ministérios Públicos. Testes SEM REDE com os itens-âncora do estudo ao vivo
(biblioteca_alexandria/base/ministerios_publicos/estudo/itens_ancora.md). As linhas da tabela seguem o formato real
devolvido pelo PRT-18 na nuvem em 02/10 (aaData: unidade, data, número, procedimento, código do PDF)."""
import json, re, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import ministerios_publicos as M

HOJE = date(2026, 10, 2)
CFG = json.loads((ROOT / "config/ministerios_publicos.json").read_text(encoding="utf-8"))
TOK = lambda n: ("zpEKILyO3R97KvSesbLpuWw4KHWh2SJL0ruqCot_iO" + n * 30)[:120]   # noqa: E731
TABELA = {"sEcho": 1, "iTotalRecords": "3", "aaData": [
    ["AN\u00c1POLIS", "01/10/2026", "009220.2026", "000037.2019.18.003-6", TOK("a")],
    ["AN\u00c1POLIS", "24/08/2026", "008314.2026", "000545.2021.18.000-2", TOK("b")],
    ["GOI\u00c2NIA", "06/08/2026", "067008.2026", "002360.2025.18.000-7", TOK("c")]]}
PDF = {TOK("a"): "EDITAL 009220.2026 Procedimento 000037.2019.18.003-6. Destinação de recursos no valor de até R$ 94.428,74 (ExTAC). "
                 "Prazo de 5 (cinco) dias. Exige cadastro prévio no Sistema de Destinações (Edital PRT18 24/2025). Interessado CPF 123.456.789-09.",
       TOK("b"): "Edital 008314.2026 — valor total de R$ 2.141.800,00. Prazo de 5 (cinco) dias. Sistema de Destinações.",
       TOK("c"): "Edital 067008.2026 — montante de R$ 40.746,65. Prazo de 5 dias. Cadastro prévio no sistema."}
HABIL = {"iTotalRecords": "57", "aaData": [["ASSOCIA\u00c7\u00c3O BENEFICENTE AUTA DE SOUZA", "06.097.682/0001-89", "Rio Verde-GO", "x"]]}
MPF = ('<ul><li><a href="/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores">'
       'MPF em Goiás cadastra entidades e órgãos públicos para recebimento de bens e valores decorrentes da atuação</a> 09/10/2025</li></ul>')


def rede_falsa(acessos):
    def _abrir(url, cfg, opener=None, dados=None, ref=None, max_bytes=0):
        acessos.append(url); M.guardar(url, cfg)            # a trava dura vale também no teste
        if "arq=" in url:
            return url.split("arq=")[1].encode()             # o "PDF" devolve o próprio código; _texto_pdf o traduz
        if "pr-go/noticias" in url:
            return MPF.encode()
        return b"<html><body>Sele\xc3\xa7\xc3\xa3o em andamento: N\xc3\xa3o h\xc3\xa1</body></html>"
    return _abrir


def tabela_falsa(pagina, task, cfg, n=200):
    return TABELA if task == "editaisdestinacaorecursosoubens" else HABIL


class TesteMotor12(unittest.TestCase):
    def ler(self, acessos, registrar=None):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        reg = registrar or mock.MagicMock(return_value={"novos": 1})
        with mock.patch.object(M, "ESTADO", Path(tmp.name) / "e.json"), mock.patch.object(M, "_abrir", rede_falsa(acessos)), \
             mock.patch.object(M, "_tabela", tabela_falsa), mock.patch.object(M, "_texto_pdf", lambda b: PDF.get(b.decode(), "")), \
             mock.patch("src.livros_regra.registrar_achados", reg), mock.patch.object(M, "robots_permite", lambda u, a: True), \
             mock.patch.object(M, "busca_doe", lambda f, h: []):
            r1 = M.ler_motor(hoje=HOJE)
            r2 = M.ler_motor(hoje=HOJE)
            est = json.loads((Path(tmp.name) / "e.json").read_text(encoding="utf-8"))
        return r1, r2, est, reg

    def test_ancoras_campos_e_classificacao(self):
        r1, _, est, _ = self.ler([])
        todos = {x.get("numero_edital"): x for x in est["abertas_registros"] + est["acompanhar"]}
        a1, a2, a3 = todos["009220.2026"], todos["008314.2026"], todos["067008.2026"]
        self.assertEqual((a1["valor"], a1["procedimento"], a1["unidade"]), ("R$ 94.428,74", "000037.2019.18.003-6", "PTM Anápolis"))
        self.assertEqual((a1["prazo_dias"], a1["prazo_tipo"], a1["data_limite_segura"]), (5, None, "2026-10-05"))
        self.assertTrue(a1["exige_cadastro"]); self.assertEqual(a1["classificacao"], "OPORTUNIDADE")
        self.assertEqual((a2["valor"], a2["procedimento"], a2["classificacao"]), ("R$ 2.141.800,00", "000545.2021.18.000-2", "ACOMPANHAR"))
        self.assertEqual((a3["valor"], a3["procedimento"], a3["classificacao"]), ("R$ 40.746,65", "002360.2025.18.000-7", "ACOMPANHAR"))
        destina = [x for x in est["abertas_registros"] if "Edital de Chamamento nº 02/2024" in str(x.get("numero_edital"))]
        self.assertEqual(len(destina), 1); self.assertTrue(destina[0]["fluxo_continuo"])                 # âncora 4: regra permanente
        mpf = [x for x in est["acompanhar"] if "bens e valores" in x["titulo"] and x["orgao"] == "MPF"]
        self.assertTrue(mpf and mpf[0]["data_publicacao"] == "2025-10-09")                                 # âncora 5: ACOMPANHAR
        self.assertTrue(all(x.get("data_consulta") == "2026-10-02" for x in est["abertas_registros"]))

    def test_negativos_sao_ruido(self):
        for t, org in (("MPDFT obtém destinação de mais de R$ 12 milhões para o Fundo de Modernização da PCDF", "MPDFT"),
                       ("Edital de Notificação nº 1 — Procuradoria de Justiça Militar em Manaus", "MPM"),
                       ("Edital FDD NAS 2023 — seleção de projetos de direitos difusos", "Ministério da Justiça e Segurança Pública")):
            self.assertEqual(M.classificar({"titulo": t, "orgao": org}, HOJE, CFG)["classificacao"], "RUIDO", t)

    def test_um_edital_em_duas_fontes_e_um_registro(self):
        a = {"orgao": "MPT-GO", "unidade": "PTM Anápolis", "numero_edital": "009220.2026", "procedimento": "000037.2019.18.003-6", "fonte": "tabela_mpt"}
        b = {**a, "fonte": "f09", "titulo": "Notícia do edital", "ultimo_link_pdf": None}
        m = M.mesclar([a, b]); self.assertEqual(len(m), 1); self.assertEqual(set(m[0]["fontes_encontradas"]), {"tabela_mpt", "f09"})
        self.assertEqual(m[0]["chave"], "MPT-GO|PTM Anápolis|009220.2026|000037.2019.18.003-6")

    def test_inventario_entra_uma_vez(self):
        _, _, est, reg = self.ler([])
        self.assertEqual(reg.call_count, 1); self.assertTrue(est["inventario"]["inventario_base_registrado"])
        self.assertGreaterEqual(len(M.inventario_base()), 70)                         # 92 do estudo, sem os de ruído

    def test_mp_go_nunca_e_acessado(self):
        acessos = []
        self.ler(acessos)
        self.assertFalse([u for u in acessos if "mpgo.mp.br" in u or "destinacoes.mpt.mp.br" in u])
        with self.assertRaises(M.AcessoProibido):
            M.guardar("https://www.mpgo.mp.br/portal/conteudo/destina", CFG)
        with self.assertRaises(M.AcessoProibido):
            M.guardar("https://destinacoes.mpt.mp.br/", CFG)

    def test_nenhum_cpf_nos_registros(self):
        r1, _, est, _ = self.ler([])
        texto = json.dumps([r1["achados"], est["abertas_registros"], est["acompanhar"]], ensure_ascii=False)
        self.assertIsNone(re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", texto))
        self.assertNotIn("123.456.789-09", json.dumps(M.registro_base({"titulo": "x CPF 123.456.789-09", "orgao": "MPT-GO"}, HOJE)))

    def test_associacao_nao_habilitada_gera_pendencia(self):
        _, _, est, _ = self.ler([])
        self.assertFalse(est["habilitadas"]["associacao_consta"]); self.assertEqual(est["habilitadas"]["total"], 57)
        self.assertTrue(any("Sistema de Destinações" in p for p in est["pendencias_presidente"]))

    def test_despacho_no_sensores(self):
        self.assertIn('if sensor.get("id") == "plat-mp-destinacoes-reparacao":', (ROOT / "src/sensores.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


DOE_DAAMP = {"hits": {"total": 1, "hits": [{"_source": {"diario_id": 7309, "pagina": 87, "data": "2026-08-07T00:00:00",
    "conteudo": "AVISO DE LICITAÇÃO O Prefeito Municipal de Itarumã/GO torna público. Objeto: Contratação de empresa especializada "
                "para aquisição de grades e implementos, destinados ao atendimento das demandas do Município de Itarumã/GO, em "
                "conformidade ao Projeto Institucional de Destinação Articulada de Acordos (DAAMP), Autos Administrativos n. 123."}}]}}


class TesteMotor08MPGO(unittest.TestCase):
    """Teste do motor 08 (MP-GO) de 03/10/2026."""

    def ler(self, verif=None):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        cfg = json.loads(json.dumps(CFG)); cfg["verificacoes_manuais"]["mpgo-destinacao"] = verif
        acessos = []
        from src import diario_goias as dg
        with mock.patch.object(M, "_cfg", return_value=cfg), mock.patch.object(M, "_abrir", rede_falsa(acessos)), \
             mock.patch.object(dg, "_get_json", side_effect=lambda url, **k: (acessos.append(url) or DOE_DAAMP)), \
             mock.patch("src.livros_regra.registrar_achados", mock.MagicMock(return_value={})), \
             mock.patch.dict(M.PARTES, {"mpgo-destinacao": ({"MP-GO"}, None, str(Path(tmp.name) / "e.json"))}):
            r = M.ler_parte("mpgo-destinacao", None, HOJE)       # o estado vai para a pasta temporária, nunca para estado/
        return r, acessos

    def test_leitura_indireta_pelo_diario_do_estado_sem_tocar_no_mp_go(self):
        r, acessos = self.ler()
        self.assertFalse([u for u in acessos if "mpgo.mp.br" in u])
        self.assertTrue(all("diariooficial.abc.go.gov.br" in u for u in acessos))
        self.assertEqual(r["diagnostico"]["fontes"]["f00b"]["situacao"], "lida")
        self.assertEqual(r["diagnostico"]["vereditos"]["ACOMPANHAR"], 1)          # Itarumã: inteligência, não ruído
        self.assertEqual(len(r["achados"]), 1)                                   # só o Destina (regra permanente) é oportunidade

    def test_pendencia_do_mpt_nao_vaza_e_conferencia_manual_e_lembrada(self):
        r, _ = self.ler()
        pend = r["diagnostico"]["pendencias_presidente"]
        self.assertFalse([p for p in pend if "Sistema de Destinações" in p])
        self.assertTrue([p for p in pend if "Destina do MP-GO" in p])
        self.assertTrue([p for p in pend if "Conferência manual mensal" in p and "ainda não registrada" in p])
        r2, _ = self.ler(verif=HOJE.isoformat())
        self.assertFalse([p for p in r2["diagnostico"]["pendencias_presidente"] if "Conferência manual mensal" in p])

    def test_leitura_do_dia_nao_diz_completa(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        cfg = json.loads(json.dumps(CFG))
        M._PARTE["id"] = "mpgo-destinacao"
        try:
            self.assertTrue(M._so_regra_fixa(cfg))
            t = M._texto_regra_fixa({"fontes": {"f00b": {"modo": "busca_doe", "situacao": "lida"}}}, cfg)
        finally:
            M._PARTE["id"] = None
        self.assertIn("proíbe robôs", t)
        self.assertIn("indireta pelo Diário do Estado: feita", t)
