"""15/10/2026 (titular): Oportunidades Abertas › Legislativo — ato legislativo é acompanhado, não gera livro."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import legislativo as L


class Legislativo(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = [mock.patch.object(L, n, self.d / f) for n, f in (("ESTADO", "leg.json"), ("ENTRADA", "entrada.json"),
                                                                    ("PAINEL", "painel.json"), ("CAMARA", "camara.json"))]
        for x in self.p:
            x.start()
        self.addCleanup(lambda: [x.stop() for x in self.p])

    def _camara(self, situacao):
        (self.d / "camara.json").write_text(json.dumps({"utilidade_publica": [{"entidade": "INSTITUTO X", "projeto": "Projeto de Lei nº 216/2026",
            "autor": "VEREADOR Y", "criado": "2026-05-19", "situacao": situacao, "setor": "Plenário", "url": "https://www.goiania.go.leg.br/p.pdf"}],
            "acompanhar": [{"titulo": "Câmara de Goiânia — Projeto da Lei Orçamentária Anual de 2027 começa a tramitar", "url": "https://www.goiania.go.leg.br/n",
                            "data_publicacao": "2026-10-02", "categoria": "orcamento_emendas"}]}), encoding="utf-8")

    def test_classificacao(self):
        self.assertEqual(L.tipo_de("Projeto de Lei nº 715/2025 declara de utilidade pública a Associação"), "Utilidade pública")
        self.assertEqual(L.tipo_de("Projeto da Lei Orçamentária Anual de 2027"), "Orçamento (LOA / emendas)")
        self.assertEqual(L.numero_de("Projeto de Lei nº 216/2026"), "PL 216/2026")
        self.assertEqual(L.situacao_de("em pauta na sessão de 2026-10-07 (segunda votação)"), "em pauta — segunda votação")

    def test_movimentacoes_sem_duplicar_e_sem_livro(self):
        with mock.patch.object(L, "_eventos", lambda m: []):
            self._camara("em pauta na sessão de 2026-09-22 (primeira votação)")
            r1 = L.atualizar()
            self._camara("em pauta na sessão de 2026-10-07 (segunda votação)")
            L.atualizar(); L.atualizar()                                  # a terceira passagem não repete movimento
        self.assertEqual(r1["proposicoes"], 2)
        pl = next(x for x in json.loads((self.d / "leg.json").read_text())["itens"].values() if x["numero"] == "PL 216/2026")
        self.assertEqual([m["situacao"] for m in pl["movimentacoes"]], ["em pauta na sessão de 2026-09-22 (primeira votação)",
                                                                        "em pauta na sessão de 2026-10-07 (segunda votação)"])
        self.assertEqual(pl["ultima_movimentacao"], "2026-10-07")
        self.assertFalse(pl["gera_livro"])
        self.assertEqual(json.loads((self.d / "painel.json").read_text())["total"], 2)

    def test_achado_legislativo_e_desviado_dos_livros(self):
        self.assertTrue(L.e_legislativo({"fonte_id": "alego-pl", "titulo": "Projeto de lei x"}))
        self.assertTrue(L.e_legislativo({"titulo": "Plenário aprova projeto de lei de fomento", "url": "https://portal.al.go.leg.br/noticias/1"}))
        self.assertFalse(L.e_legislativo({"titulo": "Edital de chamamento público 01/2026", "url": "https://www.anapolis.go.gov.br/e.pdf"}))
        L.receber({"titulo": "Projeto de Lei nº 10/2026 utilidade pública", "url": "https://portal.al.go.leg.br/n/1", "fonte_id": "alego-pl"}, "ALEGO")
        L.receber({"titulo": "Projeto de Lei nº 10/2026 utilidade pública", "url": "https://portal.al.go.leg.br/n/1", "fonte_id": "alego-pl"}, "ALEGO")
        self.assertEqual(len(json.loads((self.d / "entrada.json").read_text())["itens"]), 1)


if __name__ == "__main__":
    unittest.main()
