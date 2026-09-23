"""Mesa de captação: listas numeradas, trilhas por botão e potencial fiscal (22/09)."""
import json, pathlib, re, unittest
from src.potencial_fiscal import (estimar, faixa_texto, resumir, LEIS_IRPJ,
                                  ADICIONAL_A_PARTIR_DE, ALIQUOTA_IRPJ, MARGEM_PADRAO)
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")


class TestePotencialFiscal(unittest.TestCase):
    def test_as_seis_leis_com_seus_limites(self):
        self.assertEqual(set(LEIS_IRPJ), {"fia", "idoso", "pronon", "pronas", "rouanet", "esporte"})
        self.assertEqual(LEIS_IRPJ["rouanet"]["limite"], 0.04)          # cultura é a maior
        self.assertEqual(LEIS_IRPJ["fia"]["limite"], 0.01)
        self.assertAlmostEqual(sum(v["limite"] for v in LEIS_IRPJ.values()), 0.09, places=4)
        for k, v in LEIS_IRPJ.items():
            self.assertTrue(v["serve_para"] and v["conselho"], k)        # cada lei diz onde se entra

    def test_conta_do_irpj(self):
        e = estimar({"porte": "DEMAIS", "capital_social": "85000000", "uf": "GO"})
        self.assertTrue(e["apurou"])
        i = e["irpj"]
        self.assertGreater(i["devido_max"], i["devido_min"])
        self.assertEqual(i["teto_pct"], 9.0)
        self.assertAlmostEqual(i["direcionavel_max"], round(i["devido_max"] * 0.09), delta=2)
        self.assertEqual(e["margem_usada_pct"], round(MARGEM_PADRAO * 100, 1))
        self.assertIn("Lucro Real", i["regra"])
        self.assertEqual(ALIQUOTA_IRPJ, 0.15); self.assertEqual(ADICIONAL_A_PARTIR_DE, 240_000.0)

    def test_simples_nacional_nao_deduz(self):
        e = estimar({"porte": "ME", "opcao_simples": "Sim"})
        self.assertFalse(e["apurou"])
        self.assertIn("Simples Nacional", e["motivo"])
        self.assertEqual(e["confianca"], "certa")                        # essa nós sabemos com certeza

    def test_sem_dado_nao_inventa_numero(self):
        e = estimar({})
        self.assertFalse(e["apurou"]); self.assertIsNone(e["irpj"])
        self.assertEqual(e["confianca"], "nenhuma")
        e2 = estimar({"porte": "DEMAIS", "situacao": "BAIXADA"})
        self.assertFalse(e2["apurou"]); self.assertIn("Baixada", e2["motivo"])

    def test_icms_fica_a_confirmar_em_vez_de_chutar(self):
        e = estimar({"porte": "DEMAIS", "capital_social": "10000000", "uf": "GO"})
        self.assertEqual(e["icms"]["situacao"], "a confirmar")
        self.assertIsNone(e["icms"]["direcionavel_min"])
        self.assertIn("programa estadual", e["icms"]["porque"])

    def test_a_conta_fica_a_mostra(self):
        e = estimar({"porte": "EPP", "capital_social": "500000"})
        for c in ("base_do_calculo", "faturamento", "margem_usada_pct", "lucro_estimado", "aviso"):
            self.assertIn(c, e, c)
        self.assertIn("não para escrever em ofício", e["aviso"])

    def test_valores_arredondados_sem_precisao_falsa(self):
        self.assertEqual(faixa_texto(1_323_900_000, 10_592_900_000), "R$ 1,3 bi a R$ 10,6 bi")
        self.assertEqual(faixa_texto(12_000, 90_000), "R$ 12 mil a R$ 90 mil")
        self.assertEqual(faixa_texto(None, None), "—")


class TesteMesaDeCaptacao(unittest.TestCase):
    def test_sem_rolagem_interna_na_lista(self):
        bloco = H.split(".mz-lista{")[1].split("}")[0]
        self.assertNotIn("overflow:auto", bloco)
        self.assertNotIn("max-height", bloco)

    def test_listas_numeradas_de_cem_em_cem(self):
        self.assertIn("for(let i=0;i<lista.length;i+=100)", H)
        self.assertIn("n:cadernos.length+1", H)                          # 1, 2, 3...
        self.assertIn("mz-cd", H); self.assertIn("mesaCaderno", H)
        self.assertIn("<b>${c.n}</b><span>${c.de}–${c.ate}</span>", H)   # nº da lista e o intervalo

    def test_botao_para_cada_trilha(self):
        self.assertIn("tributaria:{rotulo:\"Destinação tributária\"", H)
        self.assertIn("privado:{rotulo:\"Patrocínio privado\"", H)
        self.assertIn("window.mesaTrilha", H)
        self.assertIn('role="tablist"', H); self.assertIn('aria-selected', H)
        self.assertIn("uma trilha por vez", H.lower().replace("\n", " "))

    def test_dinheiro_no_lugar_de_maior_peso(self):
        self.assertIn("Potencial desta lista", H)
        self.assertIn("mz-cifra", H)
        self.assertIn("IRPJ direcionável por ano", H)
        self.assertIn("somaMin", H); self.assertIn("somaMax", H)          # soma da lista visível
        self.assertIn("mz-icms", H)

    def test_a_conta_aparece_na_ficha(self):
        self.assertIn("Quanto pode direcionar, por ano", H)
        self.assertIn("Como se chegou a isso", H)
        self.assertIn("mz-leis", H); self.assertIn("mz-passos", H)
        self.assertIn("15% + 10% sobre o que passa de R$ 240 mil", H)
        self.assertIn("mz-aviso", H)

    def test_nao_promete_o_que_nao_sabe(self):
        self.assertIn("a confirmar", H)
        self.assertIn("mz-sem", H)                                       # empresa sem estimativa diz por quê
        self.assertIn("não para escrever em ofício", H)
        self.assertIn("a levantar", H)                                   # contato vazio é convite

    def test_acessivel_e_responsivo(self):
        self.assertIn('tabindex="0"', H); self.assertIn("event.key==='Enter'", H)
        self.assertIn("@media(max-width:780px)", H)
        self.assertIn("prefers-reduced-motion", H)
        self.assertIn("focus-visible", H)
