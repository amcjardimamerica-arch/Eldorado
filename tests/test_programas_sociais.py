"""Programas apoiados, numeração por lista e ordem por evidência social (23/09)."""
import json, pathlib, unittest
from src.programas_sociais import LEIS, PESOS, identificar, programas_de, pontos_sociais
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
R = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))


class TesteCatalogoDeLeis(unittest.TestCase):
    def test_as_leis_que_importam_estao_no_catalogo(self):
        for k in ("rouanet", "esporte", "fia", "idoso", "pronon", "pronas"):
            self.assertIn(k, LEIS, k)
        for k, d in LEIS.items():
            for c in ("nome", "lei", "area", "orgao", "teto", "porta", "apelidos"):
                self.assertTrue(d.get(c), f"{k}.{c}")

    def test_cada_lei_diz_por_onde_se_entra(self):
        self.assertIn("CMDCA", LEIS["fia"]["orgao"])                      # criança: conselho municipal
        self.assertIn("SALIC", LEIS["rouanet"]["orgao"])                  # cultura: projeto aprovado antes
        self.assertIn("aprovado", LEIS["rouanet"]["porta"])
        self.assertIn("paradesporto", LEIS["esporte"]["porta"])
        self.assertIn("4%", LEIS["rouanet"]["teto"]); self.assertIn("1%", LEIS["fia"]["teto"])

    def test_reconhece_o_nome_de_varias_formas(self):
        self.assertEqual(identificar("FIA"), "fia")
        self.assertEqual(identificar("Lei do Esporte"), "esporte")
        self.assertEqual(identificar("LIE"), "esporte")
        self.assertEqual(identificar("incentivo à cultura"), "rouanet")
        self.assertEqual(identificar("Fundo do Idoso"), "idoso")
        self.assertIsNone(identificar("")); self.assertIsNone(identificar("qualquer coisa"))


class TesteProgramasDaEmpresa(unittest.TestCase):
    def test_extrai_do_campo_de_incentivos(self):
        p = programas_de({"incentivos": ["FIA", "Rouanet", "Lei do Esporte"]})
        self.assertEqual(len(p), 3)
        self.assertTrue(all(x["historico"] for x in p))                    # declarado = já destinou
        self.assertTrue(all(x["porta"] and x["orgao"] for x in p))

    def test_nao_duplica_a_mesma_lei(self):
        p = programas_de({"incentivos": ["FIA", "fia", "Fundo da Criança"]})
        self.assertEqual(len([x for x in p if x["chave"] == "fia"]), 1)

    def test_mencao_no_texto_entra_como_a_confirmar(self):
        p = programas_de({"por": ["apoia projetos de oncologia pelo PRONON"]})
        self.assertTrue(p); self.assertFalse(p[0]["historico"])            # citado, não comprovado


class TestePontuacaoSocial(unittest.TestCase):
    def test_historico_pesa_mais_que_mencao(self):
        com = pontos_sociais({"incentivos": ["FIA", "Rouanet"]})
        cit = pontos_sociais({"por": ["menciona PRONON e Rouanet"]})
        self.assertGreater(com["pontos"], cit["pontos"])
        self.assertEqual(com["leis_com_historico"], 2)
        self.assertGreater(PESOS["lei_com_historico"], 4)

    def test_instituto_proprio_pesa(self):
        sem = pontos_sociais({"incentivos": ["FIA"]})
        com = pontos_sociais({"incentivos": ["FIA"], "programa": "Instituto X"})
        self.assertEqual(com["pontos"] - sem["pontos"], PESOS["instituto_proprio"])

    def test_cada_ponto_tem_justificativa(self):
        r = pontos_sociais({"incentivos": ["FIA"], "programa": "Instituto X", "apoia": "cultura"})
        self.assertTrue(r["por"])
        self.assertTrue(all(":" in x for x in r["por"]))                   # "14: já destinou por..."
        self.assertIn(r["nivel"], ("forte", "bom", "inicial", "sem evidência"))

    def test_sem_evidencia_nao_inventa_nota(self):
        r = pontos_sociais({"nome": "X"})
        self.assertEqual(r["pontos"], 0); self.assertEqual(r["nivel"], "sem evidência")


class TesteRankingPorEvidencia(unittest.TestCase):
    def test_ordem_propria_dentro_de_cada_lista(self):
        for origem in R["por_origem"]:
            L = [e for e in R["empresas"] if e["origem"] == origem]
            self.assertTrue(all(L[i]["pontos_lista"] >= L[i + 1]["pontos_lista"] for i in range(len(L) - 1)), origem)
        self.assertIn("pontuação própria", R["regra"])

    def test_numeracao_por_lista_sem_buraco(self):
        """A posição global saltava (8 → 10) porque a tela filtra por lista."""
        for origem in R["por_origem"]:
            ns = sorted(e["n_na_lista"] for e in R["empresas"] if e["origem"] == origem)
            self.assertEqual(ns, list(range(1, len(ns) + 1)), origem)
        self.assertIn("n_na_lista", R["empresas"][0])

    def test_cada_empresa_traz_seus_programas(self):
        com = [e for e in R["empresas"] if e["programas"]]
        self.assertGreater(len(com), 40)
        p = com[0]["programas"][0]
        for c in ("nome", "lei", "orgao", "teto", "porta", "historico", "prova"):
            self.assertIn(c, p, c)


class TesteTelaDeProgramas(unittest.TestCase):
    def test_coluna_de_programas_na_linha(self):
        self.assertIn("ep-prog", H); self.assertIn("ep-lei", H)
        self.assertIn('F.lista==="tributaria"?"Já destinou por":"Como apoia"', H)   # cabeçalho por lista
        self.assertIn('e.n_na_lista||e.posicao', H)                         # número da lista, não o global

    def test_ficha_abre_a_tela_dos_programas(self):
        self.assertIn("Programas de incentivo", H)   # a ficha lista as 8, com e sem registro
        self.assertIn("Como se entra:", H)                                  # a porta de cada lei
        self.assertIn("ep-prog-l", H); self.assertIn("já destinou", H)
        self.assertIn("citado — a confirmar", H)                            # distingue comprovado de citado
        self.assertIn("Nota nesta lista", H)

    def test_explica_a_ordem_ao_leitor(self):
        self.assertIn("A ordem é por evidência social, e cada lista tem a sua", H)
        self.assertIn("Como esta lista é pontuada", H)
        self.assertIn("Nota média desta página", H)

    def test_empresa_sem_programa_nao_finge(self):
        # as leis sem registro agora aparecem apagadas, em vez de a célula ficar vazia
        self.assertIn("nenhuma destinação registrada", H)
        self.assertIn("Sem registro de destinação", H)
        self.assertIn("não levantado", H)


class TesteCoresDosProgramas(unittest.TestCase):
    """Todas as leis sempre à vista: colorida quando há destinação, apagada quando não há."""

    def test_cada_lei_tem_cor_e_nome_curto_proprios(self):
        from src.programas_sociais import catalogo, ORDEM, LEIS
        cat = catalogo()
        self.assertEqual(len(cat), len(LEIS))
        self.assertEqual([c["chave"] for c in cat], ORDEM)
        cores = [c["cor"] for c in cat]
        self.assertEqual(len(cores), len(set(cores)), "cada programa precisa de uma cor própria")
        for c in cat:
            self.assertRegex(c["cor"], r"^#[0-9A-Fa-f]{6}$")
            self.assertTrue(c["curto"] and len(c["curto"]) <= 10, c["chave"])

    def test_a_primeira_e_a_de_maior_teto(self):
        from src.programas_sociais import ORDEM
        self.assertEqual(ORDEM[0], "rouanet")                  # 4% do IRPJ, a maior
        self.assertEqual(ORDEM[1], "fia")                      # a mais usada no levantamento

    def test_o_catalogo_vai_para_a_tela(self):
        self.assertIn("catalogo_de_leis", R)
        self.assertEqual(len(R["catalogo_de_leis"]), 8)
        for L in R["catalogo_de_leis"]:
            for c in ("chave", "curto", "nome", "cor", "lei", "orgao", "teto", "porta"):
                self.assertIn(c, L, c)

    def test_a_linha_mostra_todas_as_leis(self):
        self.assertIn("R.catalogo_de_leis||[]).map(L=>", H)
        self.assertIn("TODAS as leis sempre à vista", H)
        self.assertIn('nenhuma destinação registrada', H)      # o título da apagada explica
        self.assertIn("--lc:${L.cor}", H)

    def test_apagada_e_colorida_se_distinguem(self):
        self.assertIn(".ep-lei.fez{color:#fff", H); self.assertIn("background:var(--lc)", H)
        self.assertIn(".ep-lei.nao{color:#B9C3CE;background:#F5F7F9", H)
        self.assertIn(".ep-lei.cit{color:var(--lc)", H)         # citado: cor, mas tracejado

    def test_a_lista_de_doacao_tambem_usa_cores(self):
        self.assertIn("CRIT_COR", H); self.assertIn("CRIT_CURTO", H)
        self.assertIn("_corCrit", H); self.assertIn("_curtoCrit", H)

    def test_a_ficha_separa_com_registro_de_sem_registro(self):
        self.assertIn("com registro · ", H)
        self.assertIn("Sem registro de destinação", H)
        self.assertIn("não achamos registro público", H)
