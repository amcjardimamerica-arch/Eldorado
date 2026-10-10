"""10/10 (titular, motores 40 e 41): motor de coleta assistida é creditado pela ROTA INDIRETA (verde quando ela leu,
vermelho quando parou); sem rota indireta, cinza 'aguarda coleta assistida'. O Espião religa a busca do Prosas.
O robots.txt do Mapa das OSC é verificado pela nuvem, sem ler caminho proibido."""
import json, random, sys, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import status_motores as SM


class TesteRotaAssistida(unittest.TestCase):
    def _com(self, ultima_capitaai):
        cfg = [{"id": "prosas", "motor": "site-prosas", "rota": "assistida", "rota_indireta": {"site": "capitaai"}},
               {"id": "mapa-osc", "motor": "site-mapa-osc", "rota": "assistida"}]
        pub = {"capitaai": {"ultima": ultima_capitaai, "diag": {"cartoes_rota_indireta_prosas": 63}}, "prosas": {}, "mapa-osc": {}}
        self.orig = SM._indexador_do_motor
        SM._indexador_do_motor = lambda mid: (next((s for s in cfg if s["motor"] == mid), {}), pub)

    def tearDown(self):
        SM._indexador_do_motor = self.orig

    def test_prosas_verde_pela_rota_indireta_e_mapa_aguarda(self):
        self._com((datetime.now(timezone.utc) - timedelta(hours=3)).isoformat())
        luz, txt, _ = SM.rota_assistida({"id": "site-prosas"})
        self.assertEqual(luz, "verde"); self.assertIn("rota indireta (capitaai)", txt); self.assertIn("63", txt)
        self.assertEqual(SM.rota_assistida({"id": "site-mapa-osc"})[:2], ("cinza", "inativo — aguarda coleta assistida (o site proíbe robôs; sem rota indireta)"))
        self.assertIsNone(SM.rota_assistida({"id": "dou"}), "motor comum segue a regra geral")

    def test_rota_indireta_parada_e_falha(self):
        self._com((datetime.now(timezone.utc) - timedelta(hours=40)).isoformat())
        self.assertEqual(SM.rota_assistida({"id": "site-prosas"})[0], "vermelho")


class TesteEspiaoSitesFechados(unittest.TestCase):
    def test_familia_do_prosas(self):
        from src import espiao_foco as E
        f = E.familias(); self.assertIn("sites_fechados", f)
        qs = {f["sites_fechados"](random.Random(i), 2026) for i in range(20)}
        self.assertTrue(all("2026" in q for q in qs)); self.assertTrue(any("Prosas" in q for q in qs))
        self.assertFalse(any("FINEP" in q for q in qs), "FINEP (governo) fica com os motores")


class TesteRobots(unittest.TestCase):
    def test_nao_le_caminho_proibido_e_conclui(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import verificar_robots as V
        lidos = []
        def falso(url, limite=600_000):
            lidos.append(url)
            if url.endswith("/robots.txt"):
                return 200, "text/plain", "User-agent: *\nDisallow: /editais\nAllow: /api/\n"
            if "/api/" in url:
                return 200, "application/json", '[{"edital": 1}]'
            return 200, "text/html", '<a href="/x">edital</a> <script>fetch("/api/editais/abertos")</script>'
        o, V._get = V._get, falso
        try:
            r = V.verificar("https://site.gov.br", ["/editais", "/api/editais", "/"])
        finally:
            V._get = o
        self.assertNotIn("https://site.gov.br/editais", lidos, "caminho proibido não é aberto")
        self.assertIn("/api/editais", r["conclusao"]); self.assertIn("/api/editais/abertos", r["endpoints_encontrados"])


if __name__ == "__main__":
    unittest.main()
