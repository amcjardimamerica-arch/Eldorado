"""15/10/2026 (titular): os livros são o banco — cada oportunidade cria ou vincula o seu livro; eliminada some."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import banco_livros as B


class BancoLivros(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
        for d in ("biblioteca_alexandria/fontes", "dados/oportunidades/validacao_mapa", "estado/cartorio"):
            (self.r / d).mkdir(parents=True)
        (self.r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "op-antigo", "programa": "FIA Goiânia", "pagina": "https://www.goiania.go.gov.br/fia/edital-2026", "historico": [{"ano": 2025}]}]}))
        regs = [{"id": "a1", "titulo": "FIA Goiânia 2026", "url": "https://goiania.go.gov.br/fia/edital-2026", "itens": {"Objeto": {"estado": "comprovado", "valor": "x"}}},
                {"id": "b2", "titulo": "Chamamento novo", "url": "https://anapolis.go.gov.br/chamamento-7", "nota_rede": 0.8}]
        (self.r / "dados/oportunidades/repositorio_unico.json").write_text(json.dumps({"registros": regs}))
        (self.r / "estado/cartorio/certidoes.json").write_text(json.dumps({"certidoes": {"estrela:b2": {"em": "2026-10-15", "leitura": "total",
            "itens": {"Valor": {"valor": "R$ 10.000,00", "trecho": "valor global de R$ 10.000,00", "pagina": 3, "documento": "https://anapolis.go.gov.br/e.pdf"}}}}}))
        self.p = [mock.patch.object(B, "ROOT", self.r), mock.patch.object(B, "CAT", self.r / "biblioteca_alexandria/fontes/motores.json"),
                  mock.patch.object(B, "INDICE", self.r / "biblioteca_alexandria/fontes/indice_chaves.json")]
        for x in self.p:
            x.start()

    def tearDown(self):
        for x in self.p:
            x.stop()

    def test_vincula_cria_e_reune(self):
        r = B.consolidar()
        self.assertEqual((r["livros_vinculados"], r["livros_criados"]), (1, 1))
        L = {lv["id"]: lv for lv in json.loads((self.r / "biblioteca_alexandria/fontes/motores.json").read_text())["motores"]}
        self.assertEqual(L["op-antigo"]["oportunidade"]["id_repositorio"], "a1")
        self.assertEqual(L["op-antigo"]["historico"], [{"ano": 2025}])                     # o histórico do livro fica
        novo = next(lv for lv in L.values() if lv["id"] != "op-antigo")["oportunidade"]
        self.assertEqual(novo["checklist12"]["Valor"]["pagina"], 3)
        self.assertEqual({a["origem"] for a in novo["analises"]}, {"Cartório", "rede neural"})
        self.assertEqual(B.livro_da_oportunidade({"url": "https://anapolis.go.gov.br/chamamento-7"})["oportunidade"]["id_repositorio"], "b2")

    def test_eliminada_some(self):
        B.consolidar()
        (self.r / "dados/oportunidades/repositorio_unico.json").write_text(json.dumps({"registros": []}))
        r = B.consolidar()
        L = json.loads((self.r / "biblioteca_alexandria/fontes/motores.json").read_text())["motores"]
        self.assertEqual(r["livros_removidos"], 1)
        self.assertEqual([lv["id"] for lv in L], ["op-antigo"])
        self.assertNotIn("oportunidade", L[0])


if __name__ == "__main__":
    unittest.main()
