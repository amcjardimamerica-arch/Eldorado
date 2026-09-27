"""Guardas contra o que a tela não mostra (27/09)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TesteIntegridadePainel(unittest.TestCase):
    def test_gerador_nao_reescreve_o_painel(self):
        """Às 21h49 de 27/09 um voo regravou docs/dashboard.html com a cópia antiga e desfez a leitura pela API."""
        src = (ROOT / "src/dashboard_dados.py").read_text(encoding="utf-8")
        self.assertNotIn("html.write_text(t2", src)

    def test_leitura_ao_vivo_pela_api_e_reservas(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for trecho in ("REPO_API+cam", "REPO_RAW+cam", "_ETAG[cam]", "atualizarAgora", "seloVivo", "window._SAUDE"):
            self.assertIn(trecho, h, trecho)

    def test_fragmentos_grandes_so_regravados_se_mudarem(self):
        src = (ROOT / "src/dashboard_dados.py").read_text(encoding="utf-8")
        for nome in ("abertas.json", "historico.json", "previsoes.json", "empresas.json"):
            self.assertRegex(src, r'_grava_se_mudou\(pasta / "' + re.escape(nome) + '"')

    def test_prontidao_nao_roda_a_cada_gravacao_dos_pilotos(self):
        y = (ROOT / ".github/workflows/00-prontidao.yml").read_text(encoding="utf-8")
        self.assertNotIn("on: [workflow_dispatch, push]", y)
        self.assertIn("paths:", y)

    def test_saude_publicada_e_valida(self):
        from src.saude import checar
        r = checar()
        self.assertIn("alertas", r); self.assertIn("ok", r)
        json.loads((ROOT / "docs/dados/saude.json").read_text(encoding="utf-8"))

    def test_catalogo_de_opressores_sem_duplicados(self):
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8")).get("motores", [])
        ch = [re.sub(r"[^a-z0-9]", "", f"{x.get('programa')}{x.get('orgao')}".lower())[:80] for x in C]
        self.assertEqual(len(ch), len(set(ch)))


if __name__ == "__main__":
    unittest.main()
