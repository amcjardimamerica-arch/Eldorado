"""15/10/2026 (titular): expurgo — o que não é oportunidade sai por completo; o válido e as estruturas ficam intactos."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import expurgo as X

RUIM = "https://pncp.gov.br/app/editais/18557561000151/2026/136"        # pregão de outro estado
BOM = "https://pncp.gov.br/app/editais/01005727000124/2026/50"           # chamamento de OSC em Goiás


class Expurgo(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
        (self.r / "dados").mkdir(); (self.r / "docs/dados").mkdir(parents=True); (self.r / "biblioteca_alexandria/fontes").mkdir(parents=True)
        regs = [{"titulo": "MUNICIPIO DE NAZARENO — Pregão eletrônico para aquisição de equipamentos", "uf": "MG", "url": RUIM},
                {"titulo": "MUNICIPIO DE ANAPOLIS — Chamamento público de organizações da sociedade civil", "uf": "GO", "url": BOM},
                {"titulo": "Livro com as duas", "edicoes": [RUIM, BOM]}]
        (self.r / "dados/registros.json").write_text(json.dumps({"itens": regs}), encoding="utf-8")
        (self.r / "dados/base.jsonl").write_text("\n".join(json.dumps(x) for x in regs) + "\n", encoding="utf-8")
        col = {"campos": ["id", "titulo", "url"], "dic": {"titulo": ["MUNICIPIO DE NAZARENO — Pregão eletrônico", "MUNICIPIO DE ANAPOLIS — Chamamento de OSC"]},
               "linhas": [["a", 0, RUIM], ["b", 1, BOM]]}
        (self.r / "docs/dados/abertas.json").write_text(json.dumps(col), encoding="utf-8")
        (self.r / "biblioteca_alexandria/fontes/motores.json").write_text(json.dumps({"motores": [
            {"id": "op-ruim", "programa": "MUNICIPIO DE NAZARENO — Pregão eletrônico para aquisição", "uf": "MG", "pagina": RUIM},
            {"id": "op-bom", "programa": "MUNICIPIO DE ANAPOLIS — Chamamento de OSC", "uf": "GO", "pagina": BOM}]}), encoding="utf-8")
        p = self.r / "biblioteca_alexandria/oportunidades/pasta-ruim"; p.mkdir(parents=True); (p / "x.json").write_text(json.dumps({"u": RUIM}))
        p2 = self.r / "biblioteca_alexandria/oportunidades/pasta-boa"; p2.mkdir(parents=True); (p2 / "x.json").write_text(json.dumps({"u": BOM}))
        from src import repositorio_unico as R
        self.p = mock.patch.object(X, "ROOT", self.r); self.p.start()
        self.q = mock.patch.object(R, "construir", lambda gravar=True: {}); self.q.start()      # isola o repositório real
        self.d = mock.patch.object(R, "DESCARTADAS", []); self.d.start()

    def tearDown(self):
        self.p.stop(); self.q.stop(); self.d.stop()

    def test_simulacao_nao_apaga(self):
        j = X.executar(simular=True)
        self.assertEqual(j["invalidas"], 1)
        self.assertTrue((self.r / "biblioteca_alexandria/oportunidades/pasta-ruim").exists())

    def test_execucao(self):
        j = X.executar(simular=False)
        reg = json.loads((self.r / "dados/registros.json").read_text())["itens"]
        self.assertEqual([x["titulo"][:15] for x in reg], ["MUNICIPIO DE AN", "Livro com as du"])   # o livro misto fica
        self.assertEqual(len((self.r / "dados/base.jsonl").read_text().strip().splitlines()), 2)
        col = json.loads((self.r / "docs/dados/abertas.json").read_text())
        self.assertEqual([l[0] for l in col["linhas"]], ["b"])
        self.assertEqual(len(col["dic"]["titulo"]), 2)                                 # dicionário intacto
        self.assertEqual(j["livros_removidos"], ["op-ruim"])
        self.assertFalse((self.r / "biblioteca_alexandria/oportunidades/pasta-ruim").exists())
        self.assertTrue((self.r / "biblioteca_alexandria/oportunidades/pasta-boa").exists())


if __name__ == "__main__":
    unittest.main()


class Acervo16_10(unittest.TestCase):
    """16/10/2026: o histórico de edições passa pelos portões; quem não passa sai de todas as tabelas."""
    def test_expurgar_acervo(self):
        import gzip
        from src import banco as BC
        r = Path(tempfile.mkdtemp()); arq = r / "h.jsonl.gz"
        linhas = [{"_t": "__schema__", "tabela": "historico", "sql": "CREATE TABLE IF NOT EXISTS historico (chave TEXT)"}]
        for i, (tit, fin, uf) in enumerate([("Chamamento de OSC 2024", "MUNICIPIO DE ITUPEVA", "SP"), ("Fomento cultural 2023", "Secretaria de Estado da Cultura", "SP"),
                                             ("Chamamento de OSC 2022", "Prefeitura de Anápolis", "GO")]):
            linhas += [{"_t": "historico", "chave": f"c{i}", "ano": "2024", "id": f"i{i}", "titulo": tit, "financiador": fin, "uf": uf},
                       {"_t": "confirmacao", "chave": f"c{i}", "ano": "2024", "id": f"i{i}"}]
        with gzip.open(arq, "wt", encoding="utf-8") as g:
            g.write("\n".join(json.dumps(x) for x in linhas) + "\n")
        with mock.patch.object(BC, "CAMINHO_BANCO", r / "x.db"):
            res = BC.expurgar_acervo(arq)
        self.assertEqual(res["edicoes_removidas"], 1)                     # só Itupeva (município de SP)
        with gzip.open(arq, "rt", encoding="utf-8") as g:
            ficou = {json.loads(l).get("chave") for l in g if '"historico"' in l or '"confirmacao"' in l}
        self.assertEqual(ficou - {None}, {"c1", "c2"})
