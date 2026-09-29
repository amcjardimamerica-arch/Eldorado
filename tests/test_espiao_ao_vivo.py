"""29/09: a caixa do Espião no padrão da do Interceptador — o que está fazendo agora e as últimas missões, ao vivo."""
import sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteEspiaoAoVivo(unittest.TestCase):
    def test_transmissao_registra_plano_missao_resultado_e_pouso(self):
        from src import espiao_ao_vivo as A
        gravados = []
        with mock.patch.object(A, "_gravar", lambda c, forcar=False: gravados.append(dict(c)) or True):
            plano = [{"tipo": "aposta", "motor": "piloto-aberto", "_brief": {"pergunta": "editais de cultura em Goiás"}},
                     {"tipo": "descobrir", "motor": "piloto-aberto", "_alvo": {"titulo": "descobrir entidades novas"}}]
            A.decolar(plano, 3, [])
            A.missao(plano[0], 1, 2)
            A.resultado(plano[0], "editais de cultura", [{"titulo": "Edital X", "url": "https://x.org.br", "novo": True}], "2 no crivo", 1)
            A.pousar({"missoes": [1], "abates": 1, "propostas": 1}, em_corrente=True)
        self.assertEqual(gravados[0]["estado"], "em_voo"); self.assertEqual(len(gravados[0]["plano"]), 2)
        self.assertEqual(gravados[-1]["estado"], "patio"); self.assertEqual(gravados[-1]["concluidas"][0]["achados"], 1)

    def test_espiao_liga_a_transmissao_e_a_caixa_existe(self):
        p = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        for f in ("_AO.decolar(", "_AO.missao(", "_AO.resultado(", "_AO.pousar("):
            self.assertIn(f, p)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("window.lerEspiaoVivo=", h); self.assertIn("-esp-agora", h); self.assertIn("-esp-quadro", h); self.assertIn("window.htmlEspiaoQuadro=", h)

    def test_missoes_sao_a_soma_das_categorias(self):
        """30/09: o quadro mostrava 6.626 missões e as categorias não somavam esse número."""
        from src.espiao_relatorio import montar
        import json
        montar(); A = json.loads((ROOT / "docs/dados/espiao.json").read_text(encoding="utf-8"))["acumulado"]
        self.assertEqual(A["missoes"], sum(A["composicao"].values()))

    def test_aprendizado_das_buscas(self):
        from src.skills.aprendizado import aprender_consultas, PLACEHOLDER
        r = aprender_consultas(); self.assertIn("boas", r)
        self.assertTrue(PLACEHOLDER.search("a pergunta que orienta o voo organizações da sociedade civil"))


if __name__ == "__main__":
    unittest.main()
