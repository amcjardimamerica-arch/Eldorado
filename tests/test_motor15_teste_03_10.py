"""Teste do motor 15 (PNCP) em 03/10/2026: cursor de páginas (MG 53, SP 21 > teto 20), estados do dia e data de Brasília."""
import unittest
from datetime import date
from unittest import mock

from src import pncp_osc as P


class TesteMotor15(unittest.TestCase):
    def _cfg(self, cursor=None):
        return {"fonte_a": {"modalidades": [12], "max_paginas": 20, "tamanho_pagina": 50}, "_ufs_da_execucao": ["MG"],
                "_cursor_a": dict(cursor or {}), "falhas_seguidas_para_abortar_fonte": 3}

    def _diag(self):
        return {"fontes": {"A": {"falhas": [], "consultas": 0, "itens": 0}}}

    def test_teto_de_paginas_vira_cursor_e_parcial(self):
        pedidas = []
        def get(url, cfg):
            pedidas.append(int(url.split("pagina=")[1].split("&")[0])); return {"data": [], "totalPaginas": 53}
        cfg, diag = self._cfg(), self._diag()
        with mock.patch.object(P, "_get", side_effect=get):
            P.fonte_a(date(2026, 10, 3), cfg, diag)
        self.assertEqual(pedidas, list(range(1, 21)))
        self.assertEqual(cfg["_cursor_a"]["MG|12"], 21)
        self.assertEqual(diag["fontes"]["A"]["cortados"], 33)

    def test_continua_de_onde_parou_e_zera_no_fim(self):
        pedidas = []
        def get(url, cfg):
            pedidas.append(int(url.split("pagina=")[1].split("&")[0])); return {"data": [], "totalPaginas": 53}
        cfg, diag = self._cfg({"MG|12": 41}), self._diag()
        with mock.patch.object(P, "_get", side_effect=get):
            P.fonte_a(date(2026, 10, 3), cfg, diag)
        self.assertEqual(pedidas, list(range(41, 54)))
        self.assertNotIn("MG|12", cfg["_cursor_a"])
        self.assertFalse(diag["fontes"]["A"].get("cortados"))

    def test_hoje_e_de_brasilia(self):
        self.assertIsInstance(P._hoje_real(), date)


if __name__ == "__main__":
    unittest.main()
