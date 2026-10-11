"""11/10/2026 (titular): sala de controle da rede neural — cada função num instrumento com as quatro respostas (o que faz,
quando, efeito, resultado), estado pela cadência e pela faixa, anunciadores, mímico e página no Eldorado."""
import json, sys, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import sala_controle as S


class TesteEstado(unittest.TestCase):
    def test_estados(self):
        self.assertEqual(S._estado(None, 2, None, None)[0], "cinza")
        self.assertEqual(S._estado(0.5, 2, 0.9, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "verde")
        self.assertEqual(S._estado(0.5, 2, 0.75, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "amarelo")
        self.assertEqual(S._estado(0.5, 2, 0.6, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "vermelho")
        self.assertEqual(S._estado(10, 2, 0.9, None)[0], "vermelho", "parado há mais de 3× a cadência")
        self.assertEqual(S._estado(3, 2, 0.9, None)[0], "amarelo")

    def test_montar_com_dados_reais(self):
        r = S.montar()
        self.assertGreaterEqual(len(r["instrumentos"]), 18)
        for x in r["instrumentos"]:
            for k in ("faz", "efeito", "resultado", "estado", "sub", "nome"):
                self.assertIn(k, x, f"{x['id']} sem {k}")
        self.assertTrue(0 <= (r["indice_saude"] or 0) <= 100)
        self.assertEqual(len(r["mimico"]), 8)

    def test_pagina_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('id="v-neural"', h); self.assertIn('"neural"]', h); self.assertIn('data-v="neural"', h)
        self.assertIn("window.desenhaNeural", h); self.assertIn("sala_controle.json", h)
        self.assertIn("python -m src.sala_controle", (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "docs/prompts/PROMPT-SALA-DE-CONTROLE-REDE-NEURAL-2026-10-11.md").exists())
        # v2 (11/10): o datacenter vivo — sete etapas em sequência no axônio, detalhe por etapa, paralaxe leve
        for marca in ('id="nv-fluxo"', "const ETAPAS=[", "window.nvAbre", 'class="veios"', "prefers-reduced-motion"):
            self.assertIn(marca, h)
        self.assertNotIn('id="sc-anunciador"', h, "a versão 1 (usina) foi substituída")
        self.assertTrue((ROOT / "docs/prompts/PROMPT-SALA-DE-CONTROLE-2200-2026-10-11.md").exists())


if __name__ == "__main__":
    unittest.main()
