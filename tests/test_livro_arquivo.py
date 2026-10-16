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


class ChaveComPrefixo(unittest.TestCase):
    def test_estrela_e_livro(self):
        idx = {"op-123": "lv1", "captacao-118": "lv2"}
        self.assertEqual(LA.ligar("estrela:op-123", {}, idx), "lv1")
        self.assertEqual(LA.ligar("livro:captacao-118", {}, idx), "lv2")
        self.assertIsNone(LA.ligar("estrela:op-999", {}, idx))


class Candidata16_10(unittest.TestCase):
    """Entrada de descoberta ganha livro pelo portão de oportunidade, com ou sem prazo; prazo encerrado não."""
    def test_criterio(self):
        sem_prazo = {"titulo": "Instituto X abre chamamento de organizações da sociedade civil", "url": "https://institutox.org.br/edital"}
        self.assertTrue(LA._candidata(sem_prazo))
        self.assertFalse(LA._oportunidade_vigente(sem_prazo))                     # pela regra antiga, seria apagada
        self.assertFalse(LA._candidata({**sem_prazo, "fim": "2020-01-01"}))       # prazo encerrado
        self.assertFalse(LA._candidata({"titulo": "Instituto X abre vaga de estágio", "url": "https://x.org/vaga"}))


class EntradasDescoberta16_10(unittest.TestCase):
    def test_entradas_na_trava_e_no_modo_descoberta(self):
        self.assertTrue(LA.proibido("estado/agregadores/itens.json"))
        self.assertTrue(LA.proibido("estado/piloto/candidatas_do_catalogo.json"))
