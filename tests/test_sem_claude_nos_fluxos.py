"""02/10 (titular): nenhum fluxo do GitHub aciona IA Claude; estantes pausadas (acionamento externo); bronze com o
Piloto - Interceptador (Qwen 8B); o Espião indexa cada livro a um motor existente."""
import json, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteSemClaude(unittest.TestCase):
    def test_nenhum_fluxo_recebe_chave_de_ia(self):
        for f in (ROOT / ".github/workflows").glob("*.yml"):
            y = f.read_text(encoding="utf-8")
            for proibido in ("secrets.FAROL_AI_API_KEY", "secrets.ANTHROPIC_API_KEY", "anthropics/claude-code-action"):
                self.assertNotIn(proibido, y, f"{f.name}: {proibido}")

    def test_estantes_pausadas_e_bronze_com_qwen(self):
        E = json.loads((ROOT / "config/esteira.json").read_text(encoding="utf-8"))
        self.assertTrue(E["investigacao"]["pausada"]); self.assertEqual(E["investigacao"]["acionamento"], "externo")
        self.assertIn("Qwen", E["bronze"]["executor"])
        self.assertNotIn("esteira_bronze", json.loads((ROOT / "config/ia.json").read_text(encoding="utf-8"))["modelos"])
        self.assertNotIn("interceptador_local", (ROOT / "scripts/coleta_brasil.py").read_text(encoding="utf-8"))
        import importlib.util
        sp = importlib.util.spec_from_file_location("il", ROOT / "scripts/interceptador_local.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        self.assertTrue(m.main()["pausado"])                          # sem --externo, nada roda

    def test_interceptador_comeca_pela_estante_bronze(self):
        src = (ROOT / "src/interceptador.py").read_text(encoding="utf-8")
        self.assertIn("0 · estante bronze", src); self.assertIn('"Piloto - Interceptador (Qwen3-8B)"', src)

    def test_espiao_indexa_livros_a_motores(self):
        from src import indexacao_livros as X
        self.assertEqual(X.host("https://www.pncp.gov.br/app/editais/1"), "pncp.gov.br")
        self.assertIn("indexacao_livros", (ROOT / "src/piloto.py").read_text(encoding="utf-8"))
        C = {"motores": [{"id": "a", "pagina": "https://pncp.gov.br/app/editais/1/2026/3"},
                         {"id": "b", "pagina": "https://site-sem-motor.org/edital"}]}
        with mock.patch.object(X, "_j", lambda p, d: C if str(p).endswith("motores.json") else ({} if not isinstance(d, list) else d)), \
             mock.patch.object(X, "mapa_dominios", lambda: {"pncp.gov.br": {"pncp-api", "plat-prefeituras-50-go"}}):
            r = X.indexar(gravar=False)
        self.assertEqual(C["motores"][0]["indexacao"]["motores"], ["pncp-api"])          # o dono do domínio
        self.assertTrue(C["motores"][1]["indexacao"]["sem_motor"]); self.assertEqual(r["indexados"], 1)


if __name__ == "__main__":
    unittest.main()
