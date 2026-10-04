"""04/10/2026: o Piloto grava SÓ o livro em que trabalhou."""
import json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gravar_so_o_livro as G


class Teste(unittest.TestCase):
    def test_so_o_livro_do_voo(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            main = {"motores": [{"id": "L1", "v": 1}, {"id": "L2", "v": 1}, {"id": "L3", "v": 1}], "semente": "main"}
            novo = {"motores": [{"id": "L1", "v": 2}, {"id": "L2", "v": 2}, {"id": "L3", "v": 2}], "semente": "regenerada"}
            (t / "main.json").write_text(json.dumps(main)); cat = t / "cat.json"; cat.write_text(json.dumps(novo))
            rel = t / "rel"; rel.mkdir()
            (rel / "d.json").write_text(json.dumps({"voos": [{"em": datetime.now(timezone.utc).isoformat(), "alvo": {"id": "L2"}}]}))
            with mock.patch.object(G, "CAT", cat):
                r = G.run(str(t / "main.json"), str(rel))
            saida = {x["id"]: x["v"] for x in json.loads(cat.read_text())["motores"]}
        self.assertEqual(r["livros_gravados"], ["L2"])
        self.assertEqual(saida, {"L1": 1, "L2": 2, "L3": 1})          # só o L2 mudou
        self.assertEqual(json.loads(json.dumps(main))["semente"], "main")


if __name__ == "__main__":
    unittest.main()
