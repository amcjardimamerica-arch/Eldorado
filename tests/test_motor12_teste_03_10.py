"""Teste do motor 12 (Justiça Federal — SJGO) em 03/10/2026: robots.txt respeitado, rotas e léxico do chamamento real (Jataí 01/2026)."""
import unittest
from unittest import mock

from src import sensores


class TesteMotor12(unittest.TestCase):
    def setUp(self):
        self.s = next(x for x in sensores.registro() if x["id"] == "dj-trf1-go")

    def test_robots_proibe_nao_le_e_explica(self):
        abriu = []
        with mock.patch.object(sensores, "_robots_ok", return_value=False), \
                mock.patch.object(sensores, "_abrir", side_effect=lambda u, **k: abriu.append(u) or ("", u, 200)), \
                mock.patch.object(sensores.time, "sleep", lambda *_: None):
            r = sensores.ler(self.s, pausa=0)
        self.assertEqual(abriu, [])
        self.assertTrue(r["diagnostico"]["robots_proibe"])
        self.assertIn("robots.txt", r["diagnostico"]["motivo_zero"])

    def test_noticias_e_a_rota_principal(self):
        self.assertTrue(self.s["urls"][0].endswith("/sjgo/imprensa/noticias"))

    def test_lexico_reconhece_o_chamamento_de_jatai(self):
        termos, _ = sensores.lexico_camada1(self.s)
        rotulo = "edital de chamamento público - cadastramento de entidades para projetos sociais-ssj/jti"
        self.assertTrue(any(t in rotulo for t in termos))


if __name__ == "__main__":
    unittest.main()
