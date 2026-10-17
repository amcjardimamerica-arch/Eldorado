"""17/10/2026 — o índice dos livros (biblioteca_alexandria/livros/_origens.json) perdeu 8.411 de 8.412 entradas.

Medido no histórico do main: 08:13 = 8.412 entradas; 09:11 (fluxo "motores da vez") = 1 entrada.
Causa: quem regrava o índice lia com _j(ORIGENS, {}) — arquivo ilegível virava {} em silêncio — e gravava por cima só
as entradas novas; e a gravação não era atômica (fase encerrada por tempo deixava o arquivo cortado).
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import livro_arquivo as LA

INDICE = {f"estado/arquivo_{i}.json": {"inteiro": [f"op-{i:04d}", "0"], "gravado_em": "2026-10-17"} for i in range(500)}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig = LA.ORIGENS
        LA.ORIGENS = self.tmp / "_origens.json"

    def tearDown(self):
        LA.ORIGENS = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)


class TesteLeituraParaGravar(Base):
    def test_indice_cortado_ao_meio_e_erro_e_nao_vazio(self):
        texto = json.dumps(INDICE)
        LA.ORIGENS.write_text(texto[: len(texto) // 2], encoding="utf-8")      # como uma fase encerrada no meio
        with self.assertRaises(LA.IndiceIlegivel):
            LA.ler_origens_para_gravar()

    def test_indice_ausente_e_indice_novo(self):
        self.assertEqual(LA.ler_origens_para_gravar(), {})

    def test_indice_legivel_volta_inteiro(self):
        LA.ORIGENS.write_text(json.dumps(INDICE), encoding="utf-8")
        self.assertEqual(len(LA.ler_origens_para_gravar()), 500)


class TesteGravacaoAtomica(Base):
    def test_falha_no_meio_da_gravacao_preserva_o_indice_anterior(self):
        LA.ORIGENS.write_text(json.dumps(INDICE), encoding="utf-8")
        with mock.patch("os.replace", side_effect=OSError("processo encerrado")):
            with self.assertRaises(OSError):
                LA.gravar_origens({"so": {"uma": "entrada"}})
        self.assertEqual(len(json.loads(LA.ORIGENS.read_text(encoding="utf-8"))), 500)
        self.assertEqual([p.name for p in self.tmp.iterdir()], ["_origens.json"], "sobrou arquivo temporário")

    def test_gravacao_completa_substitui(self):
        LA.gravar_origens(INDICE)
        self.assertEqual(json.loads(LA.ORIGENS.read_text(encoding="utf-8")), INDICE)


class TesteQuemRegravaOIndice(Base):
    def test_absorver_nao_apaga_o_indice_quando_ele_esta_ilegivel(self):
        texto = json.dumps(INDICE)
        LA.ORIGENS.write_text(texto[:-40], encoding="utf-8")
        antes = LA.ORIGENS.read_bytes()
        with self.assertRaises(LA.IndiceIlegivel):
            LA.absorver([])
        self.assertEqual(LA.ORIGENS.read_bytes(), antes, "o índice foi regravado")

    def test_nenhum_gravador_le_o_indice_com_padrao_vazio(self):
        raiz = Path(__file__).resolve().parents[1]
        for arq in ("src/livro_arquivo.py", "src/banco_livros.py"):
            src = (raiz / arq).read_text(encoding="utf-8")
            self.assertNotIn("ORIGENS.write_text(", src, f"{arq}: gravação não atômica do índice")
        src = (raiz / "src/banco_livros.py").read_text(encoding="utf-8")
        self.assertNotIn("orig = _j(LA.ORIGENS, {})", src)


if __name__ == "__main__":
    unittest.main()
