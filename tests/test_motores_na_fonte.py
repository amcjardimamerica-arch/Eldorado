"""Correções na fonte (titular, 17/10/2026): triagem na entrada, rastro do motor, Drive, Mapas Culturais, placar."""
import json
import unittest

from src import banco_livros as B
from src import cartorio as C


class Triagem(unittest.TestCase):
    def test_ruido_encerrada_vigente(self):
        self.assertEqual(B._triagem({"titulo": "Credenciamento de empresas especializadas", "uf": "GO"}), "ruido")
        self.assertEqual(B._triagem({"titulo": "Edital de fomento cultural", "fim": "2020-01-10"}), "encerrada")
        self.assertIsNone(B._triagem({"titulo": "Edital de fomento cultural", "fim": "2099-01-10"}))


class Documentos(unittest.TestCase):
    def test_drive_vira_download(self):
        self.assertIn("uc?export=download&id=", C._download_direto("https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWx/view"))
        self.assertIn("/export?format=pdf", C._download_direto("https://docs.google.com/document/d/1AbCdEfGhIjKlMnOpQrStUvWx/edit"))
        self.assertEqual(C._download_direto("https://orgao.gov.br/edital.pdf"), "https://orgao.gov.br/edital.pdf")

    def test_mapas_culturais_pela_api(self):
        class RedeFalsa:
            def get(self, url):
                self.url = url
                return json.dumps({"files": {"rules": {"url": "https://mapa.cultura.gov.br/files/opportunity/10571/regulamento.pdf"},
                                             "downloads": [{"url": "https://mapa.cultura.gov.br/files/opportunity/10571/anexo-i.pdf"}]}}).encode(), "", None
        r = RedeFalsa()
        arqs = C._arquivos_mapas("http://mapa.cultura.gov.br", "10571", r)
        self.assertIn("findOne?id=EQ(10571)", r.url)
        self.assertEqual(arqs[0], "https://mapa.cultura.gov.br/files/opportunity/10571/regulamento.pdf")
        self.assertEqual(len(arqs), 2)


class OutrasOportunidades(unittest.TestCase):
    def test_fonte_de_municipio_de_outro_estado_e_desativada(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from src import outras_oportunidades as O
        p = Path(tempfile.mkdtemp()) / "fontes.json"
        p.write_text(json.dumps({"fontes": {"morrodochapeu.ba.gov.br": {"url": "https://morrodochapeu.ba.gov.br", "leituras": 3}}}))
        ach = {"achados": [{"url": "https://morrodochapeu.ba.gov.br/edital", "titulo": "Chamamento público da Prefeitura Municipal de Morro do Chapéu - BA",
                            "orgao": "Prefeitura Municipal de Morro do Chapéu", "uf": "BA"}]}
        with mock.patch.object(O, "FONTES", p), mock.patch("src.porta_oportunidade.motivo_para_nao_guardar",
                                                           return_value="municipal de fora de Goiás (BA)"):
            O.contabilizar(ach, {"id": "outras-oportunidades-1", "urls": []})
            O.contabilizar(ach, {"id": "outras-oportunidades-1", "urls": []})
        f = json.loads(p.read_text())["fontes"]["morrodochapeu.ba.gov.br"]
        self.assertEqual(f.get("achados", 0), 0); self.assertEqual(f["barrados"], 2); self.assertIn("desativada", f)
