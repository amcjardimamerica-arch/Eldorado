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
    def test_ordem_por_pontos_sociais(self):
        E = R["empresas"]
        self.assertTrue(all(E[i]["pontos_sociais"] >= E[i + 1]["pontos_sociais"] for i in range(len(E) - 1)))
        self.assertIn("evidência social", R["ordem"])
        self.assertGreater(R["com_historico_de_lei"], 30)
        self.assertGreater(sum(R["por_lei"].values()), 50)

    def test_numeracao_por_lista_sem_buraco(self):
        """A posição global saltava (8 → 10) porque a tela filtra por origem."""
        for origem in R["por_origem"]:
            ns = [e["n_na_lista"] for e in R["empresas"] if e["origem"] == origem]
            self.assertEqual(ns, list(range(1, len(ns) + 1)), origem)
        self.assertIn("n_na_lista", R["empresas"][0])

    def test_cada_empresa_traz_seus_programas(self):
        com = [e for e in R["empresas"] if e["programas"]]
        self.assertGreater(len(com), 80)
        p = com[0]["programas"][0]
        for c in ("nome", "lei", "orgao", "teto", "porta", "historico", "prova"):
            self.assertIn(c, p, c)


class TesteTelaDeProgramas(unittest.TestCase):
    def test_coluna_de_programas_na_linha(self):
        self.assertIn("ep-prog", H); self.assertIn("ep-lei", H)
        self.assertIn("Já destinou por", H)                                 # cabeçalho da coluna
        self.assertIn('e.n_na_lista||e.posicao', H)                         # número da lista, não o global

    def test_ficha_abre_a_tela_dos_programas(self):
        self.assertIn("Programas que esta empresa já apoiou", H)
        self.assertIn("Como se entra:", H)                                  # a porta de cada lei
        self.assertIn("ep-prog-l", H); self.assertIn("já destinou", H)
        self.assertIn("citado — a confirmar", H)                            # distingue comprovado de citado
        self.assertIn("Como se chegou à nota social", H)

    def test_explica_a_ordem_ao_leitor(self):
        self.assertIn("A ordem é por evidência social", H)
        self.assertIn("o setor fiscal sabe fazer", H)
        self.assertIn("Com histórico de destinação", H)                     # contador na página

    def test_empresa_sem_programa_nao_finge(self):
        self.assertIn("Nenhum programa levantado ainda", H)
        self.assertIn("nenhum programa levantado", H)
