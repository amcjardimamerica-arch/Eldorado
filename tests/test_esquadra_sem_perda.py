"""02/10: a esquadra é gravada a cada motor e a execução para antes do limite de tempo (o adiado volta pelo maestro)."""
import json, os, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteEsquadraSemPerda(unittest.TestCase):
    def test_parada_graciosa_e_registro_a_cada_motor(self):
        import src.sensores as S
        grav = []
        est0 = {"sensores": {"pncp-api": {"duracao_s": 900}}}
        def falso(s, *a, **k):
            return {"achados": [], "falhas": [], "saude": [], "lido_em": "2026-10-02T14:30:00+00:00", "diagnostico": {}}
        with mock.patch.dict(os.environ, {"MOTORES_BLOCO": "manual", "MOTORES_FONTES": "dou,pncp-api,do-goias", "SENSORES_PRAZO_S": "100"}), \
             mock.patch.object(S, "ler", falso), mock.patch.object(S, "load_json", lambda p: est0 if str(p).endswith("esquadra.json") else json.load(open(p))), \
             mock.patch.object(S, "write_json", lambda p, d: grav.append(str(p))), mock.patch.object(S, "registrar_dia", lambda *a, **k: None), \
             mock.patch.object(S, "append_jsonl", lambda *a, **k: None):
            r = S.run()
        self.assertIn("pncp-api", r["adiados_por_tempo"])
        self.assertEqual(r["sensores_executados"], 2)
        self.assertGreaterEqual(sum(1 for g in grav if g.endswith("esquadra.json")), 3)   # 2 motores + o fim

    def test_fluxo_avisa_falha_de_verdade(self):
        y = (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8")
        self.assertIn("python -u -m src.sensores", y); self.assertIn("PIPESTATUS[0]", y); self.assertIn("SENSORES_PRAZO_S=1380", y)


if __name__ == "__main__":
    unittest.main()
