"""Duas listas independentes, com pontuação própria (23/09)."""
import json, pathlib, unittest
from src.ranking_duplo import (avaliar_fiscal, avaliar_doadora, CRITERIOS_FISCAL, CRITERIOS_DOADORA)
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
R = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))


class TesteListasIndependentes(unittest.TestCase):
    def test_sao_duas_listas_inteiras_e_nao_uma_dividida(self):
        self.assertEqual(R["total"], 200)
        self.assertEqual(R["por_origem"]["destinação tributária"], 100)
        self.assertEqual(R["por_origem"]["doação e patrocínio"], 100)
        self.assertIn("duas listas independentes", R["regra"])

    def test_empresa_pode_estar_nas_duas(self):
        self.assertGreater(R["nas_duas_listas"], 20)
        nas_duas = [e for e in R["empresas"] if e.get("tambem_em")]
        self.assertTrue(nas_duas)
        e = nas_duas[0]
        self.assertIn(e["tambem_em"]["lista"], ("destinacao_tributaria", "patrocinio_privado"))
        self.assertGreaterEqual(e["tambem_em"]["posicao"], 1)
        # a posição numa lista não determina a da outra: são critérios diferentes
        pares = {}
        for x in nas_duas:
            pares.setdefault(x["nome"], []).append(x["n_na_lista"])
        self.assertTrue(any(len(set(v)) > 1 for v in pares.values() if len(v) == 2),
                        "se as posições fossem sempre iguais, a pontuação não seria própria")

    def test_numeracao_propria_e_contigua(self):
        for origem in R["por_origem"]:
            ns = sorted(e["n_na_lista"] for e in R["empresas"] if e["origem"] == origem)
            self.assertEqual(ns, list(range(1, len(ns) + 1)), origem)

    def test_uid_unico_por_linha(self):
        uids = [e["uid"] for e in R["empresas"]]
        self.assertEqual(len(uids), len(set(uids)))       # posicao repetia entre as listas
        self.assertIn(":", uids[0])


class TesteCriteriosDistintos(unittest.TestCase):
    def test_cada_lista_tem_criterios_proprios(self):
        f = {c[0] for c in CRITERIOS_FISCAL}
        d = {c[0] for c in CRITERIOS_DOADORA}
        self.assertNotEqual(f, d)
        self.assertIn("leis_com_historico", f); self.assertIn("capacidade", f)
        self.assertIn("patrocinio", d); self.assertIn("marketing_social", d)
        self.assertIn("valor_percentual", d)
        for c in CRITERIOS_FISCAL + CRITERIOS_DOADORA:
            self.assertTrue(c[2] and c[3], c[0])          # rótulo e o porquê de cada critério
        self.assertEqual(sum(c[1] for c in CRITERIOS_FISCAL), 100)
        self.assertEqual(sum(c[1] for c in CRITERIOS_DOADORA), 100)

    def test_recorrencia_valores_e_percentuais_sao_criterios(self):
        self.assertIn("recorrencia", {c[0] for c in CRITERIOS_FISCAL})
        self.assertIn("recorrencia", {c[0] for c in CRITERIOS_DOADORA})
        self.assertIn("valor", {c[0] for c in CRITERIOS_FISCAL})
        self.assertIn("valor_percentual", {c[0] for c in CRITERIOS_DOADORA})

    def test_a_mesma_empresa_pontua_diferente_em_cada_lista(self):
        e = {"nome": "X", "incentivos": ["FIA", "Rouanet"], "icms_goias": 5,
             "por": ["histórico público de patrocínio de eventos"], "apoia": "cultura", "gife": True}
        f, d = avaliar_fiscal(e), avaliar_doadora(e)
        self.assertNotEqual(f["pontos"], d["pontos"])
        self.assertIn("fiscal", f["porta_de_entrada"])
        self.assertIn("marketing", d["porta_de_entrada"])

    def test_criterio_sem_dado_nao_vira_zero_silencioso(self):
        r = avaliar_doadora({"nome": "Y"})
        nao = [c for c in r["criterios"] if not c["apurado"]]
        self.assertTrue(nao)
        self.assertTrue(all(c["valor"] == "não levantado" for c in nao))
        self.assertTrue(r["falta_levantar"])
        self.assertLess(r["confianca"], 1.0)
        self.assertEqual(r["nivel"], "sem evidência")

    def test_apto_separa_quem_serve_de_quem_nao(self):
        self.assertFalse(avaliar_doadora({"nome": "Z"})["apto"])
        self.assertTrue(avaliar_doadora({"nome": "Z", "gife": True})["apto"])
        self.assertTrue(avaliar_fiscal({"nome": "Z", "icms_goias": 3})["apto"])


class TesteTela(unittest.TestCase):
    def test_a_tela_usa_o_numero_da_lista(self):
        self.assertIn("${e.n_na_lista||e.posicao}", H)
        self.assertIn("fichaEmpresa('${esc(e.uid)}')", H)
        self.assertIn("x.uid===uid", H)

    def test_mostra_os_criterios_de_cada_lista(self):
        self.assertIn("Como esta lista é pontuada", H)
        self.assertIn("ep-crit-t", H)
        self.assertIn("Nota nesta lista", H)
        self.assertIn("Porta de entrada", H)

    def test_declara_o_que_nao_foi_levantado(self):
        self.assertIn("não levantado", H)
        self.assertIn("Falta levantar", H)
        self.assertIn("o vazio é do nosso levantamento, não dela", H)
        self.assertIn("Dados levantados", H)

    def test_avisa_quando_a_empresa_esta_nas_duas(self):
        self.assertIn("também está na outra lista", H)
        self.assertIn("ep-dupla-box", H)
        self.assertIn("um pelo setor fiscal, outro pelo marketing", H)

    def test_as_duas_listas_explicam_sua_finalidade(self):
        self.assertIn("não sai do caixa dela", H)
        self.assertIn("dinheiro do próprio bolso", H)
