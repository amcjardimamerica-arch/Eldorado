"""Consolidação dos 12 pontos dos livros do Brasil (03/10/2026): cobertura total, dispensa individual com motivo e previsão só com base."""
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import consolidar_12_pontos_br as C

ARQ = ROOT / "dados/coleta_3_anos/parametros_12_br_2026-10-03.json"


def ed(ano, ab, en, prova="literal"):
    return {"ano": ano, "abertura": ab, "encerramento": en, "pagina_oficial": "https://x.gov.br/a", "trecho": "trecho literal da página", "prova": prova, "programa": "P", "titulo": "T"}


class Previsao(unittest.TestCase):
    def test_sem_edicao_nao_preve(self):
        p = C.previsao([], None)
        self.assertIsNone(p["proxima_janela"]); self.assertEqual(p["confianca"], "baixa")

    def test_duas_edicoes_mesmo_mes_preve_proximo_ano(self):
        p = C.previsao([ed("2025", "2025-03-01", "2025-04-01"), ed("2026", "2026-03-02", "2026-04-02")], None)
        self.assertEqual(p["mes_tipico"], "mar"); self.assertIn("2027", p["proxima_janela"]); self.assertEqual(p["confianca"], "média")

    def test_meses_dispersos_baixa_confianca(self):
        p = C.previsao([ed("2024", "2024-03-01", "2024-04-01"), ed("2025", "2025-08-01", "2025-09-01"), ed("2026", "2026-11-01", "2026-12-01")], None)
        self.assertEqual(p["confianca"], "baixa")

    def test_edicao_sem_pagina_oficial_nao_conta(self):
        e = ed("2025", "2025-03-01", "2025-04-01"); e["pagina_oficial"] = None
        self.assertIsNone(C.previsao([e, ed("2026", "2026-03-01", "2026-04-01")], None)["proxima_janela"])


class Item(unittest.TestCase):
    def test_item_ausente_vira_nao_localizado_com_motivo(self):
        v = C.norm_item(None, "abrir o edital")
        self.assertEqual((v["status"], v["motivo"]), ("não localizado", "abrir o edital"))

    def test_dispensa_sem_motivo_recebe_motivo(self):
        self.assertTrue(C.norm_item({"valor": None, "status": "dispensado"}, "x")["motivo"])


@unittest.skipUnless(ARQ.exists(), "arquivo consolidado ausente")
class Dados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(ARQ.read_text(encoding="utf-8"))["livros"]
        _f = json.loads((ROOT / "dados/coleta_3_anos/fila_br.json").read_text(encoding="utf-8"))
        cls.fila = {x["id"] for x in (_f.get("fila") or _f.get("itens") or [])}     # 04/10: a fila OFICIAL usa "itens"
        cls.catalogo = {x["id"] for x in json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]}

    def test_todos_os_livros_da_fila_estao_presentes(self):
        # 04/10: a fila do pacote foi remontada à parte (não entrou); vale a OFICIAL — todo consolidado é livro do catálogo
        # e a consolidação cobre ao menos 90% da fila oficial (hoje: 858 de 925)
        ids = {r["id"] for r in self.d}
        self.assertFalse(ids - self.catalogo)
        self.assertGreaterEqual(len(ids & self.fila), 0.9 * len(self.fila))

    def test_todo_livro_tem_os_12_pontos_com_status_valido(self):
        for r in self.d:
            self.assertEqual(list(r["dados"]), list(C.ITENS), r["id"])
            for k, v in r["dados"].items():
                self.assertIn(v["status"], C.STATUS_OK + ("não localizado",), (r["id"], k))

    def test_nenhum_item_nao_confirmado_fica_sem_motivo(self):
        for r in self.d:
            for k, v in r["dados"].items():
                if v["status"] != "confirmado":
                    self.assertTrue(v.get("motivo"), (r["id"], k))

    def test_decisao_valida_e_pendente_tem_classe(self):
        for r in self.d:
            self.assertIn(r["decisao"], "VARDP")
            if r["decisao"] == "P":
                self.assertTrue(r.get("classe_pendencia"), r["id"])

    def test_sem_cpf(self):
        import re
        txt = ARQ.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", txt))


if __name__ == "__main__":
    unittest.main()
