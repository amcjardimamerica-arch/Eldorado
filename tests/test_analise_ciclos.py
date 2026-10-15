"""15/10/2026 (titular): Analise o sistema — workflow, decisões por etapa e ciclos de análise com janelas."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import analise_ciclos as AC


def _prob(lista, codigo, gravidade, texto, correcao=None, quantidade=None, exemplos=None):
    lista.append({"codigo": codigo, "gravidade": gravidade, "texto": texto, "correcao": correcao, "quantidade": quantidade, "exemplos": exemplos or []})


class Ciclos(unittest.TestCase):
    def setUp(self):
        self.p = mock.patch.object(AC, "CICLOS", Path(tempfile.mkdtemp()) / "c.json"); self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_janela_comparacao_e_proxima_janela(self):
        prs = [{"number": 227, "title": "Retentativa", "merged_at": "2026-10-15T11:40:00Z"},
               {"number": 100, "title": "antiga", "merged_at": "2026-10-01T00:00:00Z"}]
        gh = lambda caminho: prs
        anterior = {"em": "2026-10-15T08:42:58+00:00", "problemas": [{"codigo": "fluxo_falhando"}, {"codigo": "sem_prazo"}]}
        d1 = {"problemas": [{"codigo": "fluxo_falhando", "correcao": "investigar o fluxo (sem correção automática)", "quantidade": 4},
                            {"codigo": "link_acesso_como_oficial", "correcao": "buscar a fonte oficial", "quantidade": 64}]}
        c1 = AC.registrar_ciclo(d1, [], gh, anterior)
        self.assertEqual(c1["n"], 1)
        self.assertEqual([c["pr"] for c in c1["correcoes_implantadas_na_janela"]], [227])     # só o que entrou na janela
        cp = c1["comparacao_com_o_ciclo_anterior"]
        self.assertEqual((cp["resolvidos"], cp["persistem"], cp["novos"]), (["sem_prazo"], ["fluxo_falhando"], ["link_acesso_como_oficial"]))
        self.assertEqual(cp["sem_diagnostico_de_correcao"], ["fluxo_falhando"])
        self.assertEqual(c1["proxima_janela_comeca_em"], "2026-10-15T11:40:00Z")              # começa na implantação
        c2 = AC.registrar_ciclo({"problemas": []}, [], lambda c: [], None)
        self.assertEqual((c2["n"], c2["de"]), (2, "2026-10-15T11:40:00Z"))
        self.assertEqual(sorted(c2["comparacao_com_o_ciclo_anterior"]["resolvidos"]), ["fluxo_falhando", "link_acesso_como_oficial"])

    def test_decisao_nao_conferida_sem_recibo(self):
        P = []
        with mock.patch.object(AC, "_abertas", lambda: []), mock.patch.object(AC, "_j", lambda p, padrao=None: padrao if padrao is not None else {}):
            out = AC.decisoes(P, _prob)
        dec = next(x for x in out if x["etapa"] == "decidir")
        self.assertTrue(dec["veredito"].startswith("não conferido"))

    def test_agregador_como_link_oficial_e_incorreto(self):
        P = []
        ab = [{"id": "a", "titulo": "Prêmio X", "link_oficial": "https://editaisdobrasil.com/x", "orgao": "Ministério"}]
        with mock.patch.object(AC, "_abertas", lambda: ab):
            out = AC.decisoes(P, _prob)
        so = next(x for x in out if x["etapa"] == "site_oficial")
        self.assertEqual((so["veredito"], so["incorretos"]), ("incorreto", 1))
        self.assertIn("decisao_site_oficial", [p["codigo"] for p in P])


if __name__ == "__main__":
    unittest.main()
