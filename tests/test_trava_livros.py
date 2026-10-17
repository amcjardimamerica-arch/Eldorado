"""Trava dos livros (titular, 17/10/2026): livro criado não é apagado nem sobrescrito; só recebe informação nova."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import trava_livros as T


class TravaDosLivros(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
        (self.r / "biblioteca_alexandria/fontes").mkdir(parents=True); (self.r / "biblioteca_alexandria/livros").mkdir(parents=True)
        self.cat = self.r / T.CAT_REL
        self.cat.write_text(json.dumps({"motores": [
            {"id": "a", "programa": "PNAB Goiás", "orgao": "Secult-GO", "pagina": "https://goias.gov.br/pnab",
             "historico": [{"id": "e1"}, {"id": "e2"}], "coleta": {"x": 1}, "estado": "aberto"},
            {"id": "b", "programa": "Fundo do Idoso", "orgao": "Conanda"},
            {"id": "c", "programa": "PNAB Goiás (cópia)", "orgao": "Secult-GO"}]}))
        (self.r / "biblioteca_alexandria/livros/a.json").write_text(json.dumps({"id": "a", "anexos": {"edital": "u1"}}))
        g = lambda *a: subprocess.run(["git", *a], cwd=self.r, capture_output=True, check=True)  # noqa: E731
        g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t"); g("add", "-A"); g("commit", "-qm", "base")
        self.p = [mock.patch.object(T, "ROOT", self.r), mock.patch.object(T, "ARQUIVADOS", self.r / "biblioteca_alexandria/livros/_arquivados"),
                  mock.patch.object(T, "REGISTRO", self.r / "estado/trava_livros.json")]
        for x in self.p:
            x.start()

    def tearDown(self):
        for x in self.p:
            x.stop()

    def test_nada_se_perde_so_se_acrescenta(self):
        # o sistema: apaga "b" (sem união), une "c" em "a", troca a página de "a", tira um item do histórico,
        # muda o estado (operacional), acrescenta informação nova e apaga o arquivo do livro "a"
        self.cat.write_text(json.dumps({"motores": [
            {"id": "a", "programa": "PNAB Goiás", "orgao": "Secult-GO", "pagina": "https://goias.gov.br/pnab-2026",
             "historico": [{"id": "e2"}, {"id": "e3"}], "coleta": {"y": 2}, "estado": "fechado", "juntados": [{"id": "c"}]}]}))
        (self.r / "biblioteca_alexandria/livros/a.json").unlink()
        st = T.aplicar()
        L = {x["id"]: x for x in json.loads(self.cat.read_text())["motores"]}
        self.assertIn("b", L, "livro apagado sem união volta")
        self.assertNotIn("c", L); self.assertTrue((self.r / "biblioteca_alexandria/livros/_arquivados/c.json").exists(), "unido: guardado inteiro")
        a = L["a"]
        self.assertEqual(a["pagina"], "https://goias.gov.br/pnab-2026", "o valor novo fica")
        self.assertEqual(a["_anteriores"]["pagina"][0]["valor"], "https://goias.gov.br/pnab", "o anterior é guardado")
        self.assertEqual({h["id"] for h in a["historico"]}, {"e1", "e2", "e3"}, "histórico só ganha")
        self.assertEqual(a["coleta"], {"y": 2, "x": 1}, "coleta só ganha")
        self.assertEqual(a["estado"], "fechado", "campo operacional muda normalmente")
        self.assertTrue((self.r / "biblioteca_alexandria/livros/a.json").exists(), "arquivo do livro apagado volta")
        self.assertEqual(st["livros_devolvidos"], 1); self.assertEqual(st["livros_arquivados_por_uniao"], 1)

    def test_sem_mudanca_nao_mexe(self):
        st = T.aplicar()
        self.assertFalse(any(st.values()))
