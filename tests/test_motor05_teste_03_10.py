"""Teste do motor 05 (ALEGO) em 03/10/2026: rota do SPL, Brasil-only, vetos do noticiário e cobertura honesta no maestro."""
import json
import os
import unittest
from unittest import mock

from src import maestro, sensores
from src.nucleo import ROOT


class TesteMotor05(unittest.TestCase):
    def setUp(self):
        cfg = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        self.cfg = cfg
        self.s = next(x for x in sensores.registro() if x["id"] == "alego-pl")

    def test_spl_e_rota_principal_e_exige_brasil(self):
        self.assertTrue(self.s["urls"][0].startswith("https://alegodigital.al.go.leg.br/spl/"))
        self.assertIn("alegodigital.al.go.leg.br", self.cfg["exige_brasil"]["dominios"])

    def test_vetos_do_noticiario(self):
        _, vetos = sensores.lexico_camada1(self.s)
        for v in ("título de cidadania", "requerimento", "moção"):
            self.assertIn(v, vetos)

    def test_maestro_nao_chama_de_completa_leitura_sem_a_parte_local(self):
        reg = {"cor": "azul", "falhas": 0}
        self.assertEqual(maestro.cobertura("alego-pl", reg, {}, {"rotas_pendentes_local": ["https://alegodigital.al.go.leg.br/spl/x"]}), "pendente_local")
        self.assertEqual(maestro.cobertura("alego-pl", reg, {}, {}), "completa")

    def test_na_nuvem_le_noticias_e_deixa_o_spl_para_a_coleta_local(self):
        lidas = []
        def abrir(url, **k):
            lidas.append(url); return ("<html></html>", url, 200)
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False), mock.patch.object(sensores, "_abrir", side_effect=abrir), \
                mock.patch.object(sensores.time, "sleep", lambda *_: None):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            r = sensores.ler(self.s, pausa=0)
        self.assertFalse(any("alegodigital" in u for u in lidas))
        self.assertTrue(r["diagnostico"].get("rotas_pendentes_local"))


if __name__ == "__main__":
    unittest.main()
