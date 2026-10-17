"""17/10/2026 — a gravação dos fluxos copiava o índice dos livros INTEIRO por cima do main.

Duas execuções simultâneas: a que terminava por último apagava o que a outra tinha acrescentado (o índice ficou em 263
entradas depois de cair para 1). A gravação agora junta os índices: nada do main se perde; o do fluxo prevalece.
"""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gsa", RAIZ / "scripts/gravar_somente_alterados.py")
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
REL = "biblioteca_alexandria/livros/_origens.json"


class TesteJuntaIndice(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); self._root = G.ROOT; G.ROOT = self.tmp / "repo"
        (G.ROOT / REL).parent.mkdir(parents=True)

    def tearDown(self):
        G.ROOT = self._root; shutil.rmtree(self.tmp, ignore_errors=True)

    def _gravar(self, main: dict, fluxo: dict) -> dict:
        (G.ROOT / REL).write_text(json.dumps(main), encoding="utf-8")
        o = self.tmp / "fluxo.json"; o.write_text(json.dumps(fluxo), encoding="utf-8")
        G._copiar(o, REL)
        return json.loads((G.ROOT / REL).read_text(encoding="utf-8"))

    def test_fluxo_concorrente_nao_apaga_entradas_do_main(self):
        main = {f"estado/a{i}.json": {"inteiro": ["op-1", str(i)]} for i in range(8000)}
        fluxo = {"estado/novo.json": {"inteiro": ["op-2", "0"]}}          # fluxo que partiu de um índice menor
        junto = self._gravar(main, fluxo)
        self.assertEqual(len(junto), 8001)

    def test_entrada_regravada_pelo_fluxo_prevalece(self):
        junto = self._gravar({"x": {"inteiro": ["op-velho", "0"]}}, {"x": {"inteiro": ["op-novo", "0"]}})
        self.assertEqual(junto["x"]["inteiro"][0], "op-novo")

    def test_indice_ilegivel_nao_e_gravado(self):
        (G.ROOT / REL).write_text('{"cortado": ', encoding="utf-8")
        o = self.tmp / "f.json"; o.write_text("{}", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            G._copiar(o, REL)

    def test_outros_arquivos_seguem_substituidos(self):
        (G.ROOT / "estado").mkdir(parents=True); (G.ROOT / "estado/x.json").write_text('{"a":1}', encoding="utf-8")
        o = self.tmp / "x.json"; o.write_text('{"b":2}', encoding="utf-8")
        G._copiar(o, "estado/x.json")
        self.assertEqual(json.loads((G.ROOT / "estado/x.json").read_text(encoding="utf-8")), {"b": 2})


if __name__ == "__main__":
    unittest.main()
