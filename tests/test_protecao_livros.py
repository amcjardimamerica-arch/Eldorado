"""Proteção do catálogo dos livros (titular, 17/10/2026): retirada em massa sem motivo é devolvida na hora."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import comando as C


class Protecao(unittest.TestCase):
    def _cat(self, n):
        return json.dumps({"motores": [{"id": f"lv-{i}", "programa": f"P{i}"} for i in range(n)]}).encode()

    def test_retirada_em_massa_volta(self):
        d = Path(tempfile.mkdtemp()); cat = d / "motores.json"; prot = d / "protecao.json"
        antes = self._cat(1000); cat.write_bytes(self._cat(300))
        with mock.patch.object(C, "_CAT_LIVROS", cat), mock.patch.object(C, "PROTECAO", prot):
            r = C._proteger_livros("fase_x", ["python", "-m", "src.algo"], antes)
        self.assertEqual(r["livros_devolvidos"], 700)
        self.assertEqual(len(json.loads(cat.read_text())["motores"]), 1000)
        self.assertEqual(json.loads(prot.read_text())["ocorrencias"][-1]["etapa"], "fase_x")

    def test_queda_pequena_segue(self):
        d = Path(tempfile.mkdtemp()); cat = d / "motores.json"
        antes = self._cat(2000); cat.write_bytes(self._cat(1933))          # −67: a consolidação
        with mock.patch.object(C, "_CAT_LIVROS", cat), mock.patch.object(C, "PROTECAO", d / "p.json"):
            r = C._proteger_livros("livros", ["python"], antes)
        self.assertNotIn("livros_devolvidos", r)
        self.assertEqual(len(json.loads(cat.read_text())["motores"]), 1933)
