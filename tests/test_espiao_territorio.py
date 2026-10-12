"""12/10/2026 (titular): o Piloto Espião prospecta empresas e oportunidades de GOIÁS; exceções: abrangência nacional e
oportunidades internacionais; não prospecta empresas internacionais."""
import json, random, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import espiao_foco as E


class TesteTerritorio(unittest.TestCase):
    def test_lista_oficial(self):
        T = json.loads((ROOT / "config/territorio_goias.json").read_text(encoding="utf-8"))
        self.assertEqual(T["total"], 246); self.assertIn("Abadia de Goiás", T["municipios"]); self.assertEqual(len(T["outros_estados"]), 26)

    def test_classificacao(self):
        f = lambda t, x="", fr="": E.territorio(t, x, "", fr)[0]
        self.assertEqual(f("Edital de patrocínio para projetos sociais em Goiânia"), "goias")
        self.assertEqual(f("Chamada de projetos", "organizações de Anápolis e Rio Verde"), "goias")
        self.assertEqual(f("Edital Cultural Trindade-GO"), "goias")
        self.assertEqual(f("Edital do instituto", "OSC de todo o Brasil podem se inscrever"), "nacional")
        self.assertEqual(f("Global grants", "call for proposals", "internacional"), "internacional")
        self.assertEqual(E.territorio("Edital — Belo Horizonte", "Minas Gerais")[:2], ("outro_estado", "MG"))
        self.assertEqual(f("Chamada pública instituto - SP"), "outro_estado")
        # nomes ambíguos (Pará/para, Natal, Vitória…) só contam com a sigla ou "estado do"
        self.assertEqual(f("Programa de apoio", "inscrições abertas para ONGs"), "indefinido")
        self.assertEqual(f("Campanha de Natal", "entidades de Goiânia"), "goias")
        self.assertEqual(f("Edital — Natal/RN"), "outro_estado")
        self.assertEqual(f("Chamada", "organizações do estado do Pará"), "outro_estado")

    def test_empresa_internacional_nao_entra(self):
        self.assertTrue(E.empresa_internacional("https://www.globalcorp.com/csr", "supports communities worldwide"))
        self.assertFalse(E.empresa_internacional("https://www.empresa.com.br/instituto", "instituto"))
        self.assertFalse(E.empresa_internacional("https://www.empresa.com/br", "atuação no Brasil"))

    def test_consultas_so_goias_ou_nacional(self):
        r = random.Random(3); fams = E.familias()
        for _ in range(60):
            for f in ("setor_apoio_regiao", "publico_apoio_empresa", "rastro_de_patrocinio", "operador_avancado", "premio_empresarial"):
                q = fams[f](r, "2026")
                self.assertRegex(q, r"Goiás|Goiânia|Brasil|nacional", q)
                self.assertNotIn("Centro-Oeste", q)

    def test_missao_descarta_outro_estado_e_empresa_internacional(self):
        src = (ROOT / "src/espiao_foco.py").read_text(encoding="utf-8")
        self.assertIn('if terr == "outro_estado":', src); self.assertIn("fora de Goiás (", src)
        self.assertIn('fr != "internacional" and not empresa_internacional(url, texto)', src)
        self.assertIn('"territorio": terr', src)


if __name__ == "__main__":
    unittest.main()
