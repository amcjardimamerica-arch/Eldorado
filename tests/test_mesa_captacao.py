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


class TesteTelaDeEmpresas(unittest.TestCase):
    """A tela refeita do zero: duas listas, sem duplicação, sem rolagem interna."""

    def test_existe_uma_unica_lista_na_tela(self):
        self.assertEqual(H.count('id="rank-apoiadores"'), 1)
        for velho in ("rk-lista", "rk-busca", "rk-bt-fiscal", "desenhaRanking", "_rkDados",
                      "mz-lista", "rk2-linha"):
            self.assertNotIn(velho, H, f"resto do ranking antigo: {velho}")

    def test_so_duas_listas_sem_o_piloto(self):
        self.assertIn('tributaria:{rot:"Destinação tributária"', H)
        self.assertIn('doadoras:{rot:"Empresas doadoras"', H)
        bloco = H.split("const LISTAS={")[1].split("};")[0]
        self.assertNotIn("Piloto", bloco)
        self.assertNotIn("prospecção", bloco)
        src = (ROOT / "src/ranking_apoiadores.py").read_text(encoding="utf-8")
        self.assertIn("As descobertas do Piloto NÃO entram aqui", src)
        r = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))
        self.assertEqual(set(r["por_origem"]), {"destinação tributária", "patrocínio privado"})

    def test_paginas_numeradas_de_cem_em_cem(self):
        self.assertIn("for(let i=0;i<filtradas.length;i+=100)", H)
        self.assertIn("n:paginas.length+1", H)
        self.assertIn("<b>${x.n}</b><span>${x.de}–${x.ate}</span>", H)
        self.assertIn("window.empPagina", H)

    def test_sem_rolagem_interna(self):
        bloco = H.split(".ep-lista{")[1].split("}")[0]
        self.assertNotIn("overflow", bloco); self.assertNotIn("max-height", bloco)

    def test_cada_linha_traz_o_que_decide(self):
        for campo in ("ep-pos", "ep-nome", "ep-ativ", "ep-porte", "ep-valor", "ep-ct"):
            self.assertIn(campo, H, campo)
        self.assertIn("c.cnpj", H); self.assertIn("c.cnae_principal", H)
        self.assertIn("c.municipio", H); self.assertIn("capital", H)
        self.assertIn("direcionavel_min", H)

    def test_filtros_relevantes(self):
        for f in ("ep-q", "ep-uf", "ep-pt", "ep-so", "empLimpa"):
            self.assertIn(f, H, f)
        self.assertIn('value="contato"', H); self.assertIn('value="valor"', H); self.assertIn('value="goias"', H)

    def test_clique_e_teclado_sem_erro(self):
        self.assertIn("onclick=\"fichaEmpresa(${e.posicao})\"", H)
        self.assertIn("window.fichaEmpresa", H)
        self.assertIn("window.fichaApoiador=window.fichaEmpresa", H)   # nome antigo não quebra
        self.assertIn("event.stopPropagation()", H)                     # link não dispara a ficha
        self.assertIn('role="button"', H); self.assertIn("aria-label=", H)

    def test_nao_perdeu_funcao_vizinha(self):
        for f in ("desenhaDocumentos", "desenhaPerfis", "ligaDropzones", "TIPOS_DOC", "abrangenciaLocal"):
            self.assertIn(f, H, f)


