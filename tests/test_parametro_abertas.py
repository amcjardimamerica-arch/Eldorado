"""11/10/2026 (titular): parâmetro único — abertas = validadas + em verificação + validação manual; fechadas por
veredito e prazos vencidos ficam fora; a tela inicial usa o mesmo número."""
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.fluxo_oportunidades import aplicar_parametro


class TesteParametro(unittest.TestCase):
    def test_estados_e_exclusoes(self):
        itens = [{"id": "a", "confirmada": True, "fim": "2026-12-01"}, {"id": "b"}, {"id": "c"}, {"id": "d"}, {"id": "e", "fim": "2026-01-01"}, {"id": "f"}]
        ver = {"b": {"veredito": "ouro"}, "c": {"veredito": "validacao_manual"}, "d": {"veredito": "ruido"}}
        ab, p = aplicar_parametro(itens, ver, "2026-10-11")
        self.assertEqual({x["id"]: x["estado"] for x in ab}, {"a": "validada", "b": "validada", "c": "validacao_manual", "f": "em_verificacao"})
        self.assertEqual((p["abertas"], p["validadas"], p["em_verificacao"], p["validacao_manual"]), (4, 2, 1, 1))
        self.assertEqual(p["abertas"], p["validadas"] + p["em_verificacao"] + p["validacao_manual"])
        self.assertEqual(p["fora_do_parametro"], {"fechada por veredito": 1, "prazo vencido": 1})

    def test_tela_inicial_usa_o_parametro(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('const PR=FX.parametro||', h); self.assertIn('"Oportunidades abertas",`${PR.abertas}`', h)
        self.assertIn('fr(PR.validadas,PR.abertas)', h)


if __name__ == "__main__":
    unittest.main()
