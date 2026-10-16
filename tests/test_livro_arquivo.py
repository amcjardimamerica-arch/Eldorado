"""16/10/2026 (titular): livro em arquivo próprio; absorção dos bancos paralelos; leitura remontada a partir dos livros."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import livro_arquivo as LA


class Absorcao(unittest.TestCase):
    def test_absorver_e_remontar(self):
        r = Path(tempfile.mkdtemp())
        (r / "biblioteca_alexandria/fontes").mkdir(parents=True); (r / "dados/x").mkdir(parents=True)
        (r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "lv1", "programa": "FIA Goiânia", "orgao": "Prefeitura de Goiânia", "pagina": "https://goiania.go.gov.br/fia"}]}))
        arq = r / "dados/x/itens.json"
        arq.write_text(json.dumps({"https://goiania.go.gov.br/fia": {"Objeto": {"valor": "FIA"}}, "https://outro.com/nada": {"Objeto": {}}}))
        with mock.patch.object(LA, "ROOT", r), mock.patch.object(LA, "PASTA", r / "biblioteca_alexandria/livros"), \
                mock.patch.object(LA, "ORIGENS", r / "biblioteca_alexandria/livros/_origens.json"), \
                mock.patch.object(LA, "CAT", r / "biblioteca_alexandria/fontes/motores.json"):
            res = LA.absorver([arq])
            self.assertFalse(arq.exists())                                                   # o banco paralelo foi apagado
            self.assertEqual(res["absorvidas"], 1)
            self.assertEqual(LA.carregar(arq), {"https://goiania.go.gov.br/fia": {"Objeto": {"valor": "FIA"}}})   # remontado
            self.assertIn("dados/x/itens.json", LA.ler("lv1")["acervo"])


if __name__ == "__main__":
    unittest.main()


class BriefingNosLivros(unittest.TestCase):
    def test_alvo_no_livro_e_memoria_de_voo_no_controle(self):
        r = Path(tempfile.mkdtemp()); (r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        (r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "lv1", "programa": "FIA Goiânia", "pagina": "https://goiania.go.gov.br/fia"}]}))
        with mock.patch.object(LA, "ROOT", r), mock.patch.object(LA, "PASTA", r / "biblioteca_alexandria/livros"), \
                mock.patch.object(LA, "ORIGENS", r / "biblioteca_alexandria/livros/_origens.json"), \
                mock.patch.object(LA, "CAT", r / "biblioteca_alexandria/fontes/motores.json"):
            a = r / "estado/piloto/briefings/1.json"
            LA.guardar(a, {"aposta": "FIA", "resultado": {"alvos": [{"nome": "FIA", "url": "https://goiania.go.gov.br/fia"}]}}, controle_sem_livro=True)
            self.assertFalse(a.exists())
            b = LA.carregar(a, {})
            self.assertEqual((b["aposta"], b["resultado"]["alvos"][0]["nome"]), ("FIA", "FIA"))
            self.assertIn("estado/piloto/briefings/1.json", LA.ler("lv1")["acervo"])
            c = r / "estado/piloto/briefings/2.json"                        # voo sem alvo ligado: a memória fica
            LA.guardar(c, {"aposta": "empresas de GO", "diagnostico": "x"}, controle_sem_livro=True)
            self.assertEqual(LA.carregar(c, {})["aposta"], "empresas de GO")
            self.assertTrue(LA.proibido("estado/piloto/briefings/x.json"))
            self.assertFalse(LA.proibido("dados/associacoes/amc/x.json"))
