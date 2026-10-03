"""Teste do motor 18 (GIFE/Capta) em 03/10/2026: alerta de prazo curto e dia de Brasília."""
import unittest
from datetime import date

from src import gife_editais as G

HOJE = date(2026, 10, 3)


class TesteMotor18(unittest.TestCase):
    def _m(self, txt):
        return {"titulo": "Edital Rede Memória Viva", "texto": txt, "publicado": "2026-09-28", "prazo_campo": None, "regiao": None}

    def test_vence_hoje_sobe_com_alerta(self):
        c = G.classificar_item(self._m("Organizações da sociedade civil de todo o Brasil podem se inscrever até o dia 3 de outubro de 2026."), HOJE)
        self.assertEqual(c["veredito"], "OPORTUNIDADE")
        self.assertTrue(c.get("alerta_prazo"))
        self.assertIn("URGENTE", c["motivos"][0])

    def test_prazo_longo_sem_alerta(self):
        c = G.classificar_item(self._m("Organizações da sociedade civil de todo o Brasil podem se inscrever até o dia 19 de outubro de 2026."), HOJE)
        self.assertEqual(c["veredito"], "OPORTUNIDADE")
        self.assertFalse(c.get("alerta_prazo"))
        self.assertEqual(c["dias_restantes"], 16)

    def test_hoje_brasilia(self):
        self.assertIsInstance(G._hoje_real(), date)


if __name__ == "__main__":
    unittest.main()
