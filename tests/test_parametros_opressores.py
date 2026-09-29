"""Os 12 parâmetros dos Motores Opressores (29/09/2026): arquivo de dados, regras de fonte e aplicação idempotente."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src import parametros_opressores as PO

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "dados/opressores/parametros/parametros_2026-09-29.json"
PROIBIDAS = ("queridodiario", "pncp.gov.br/app", "observatorio3setor", "captadores.org", "bussolasocial",
             "prosas.com.br", "idis.org.br", "filantropia.ong", "capitaai", "farolcultural", "duckduckgo")


class TestArquivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(ARQ.read_text(encoding="utf-8"))
        cls.itens = cls.d["itens"]

    def test_dez_blocos_e_todos_decididos(self):
        self.assertEqual(len(self.d["blocos"]), 10)
        self.assertGreaterEqual(len(self.itens), 300)
        self.assertEqual(len({r["id"] for r in self.itens}), len(self.itens), "id repetido")
        self.assertEqual(sum(self.d["contagem"].values()), len(self.itens))
        for r in self.itens:
            self.assertIn(r["decisao"], PO.DECISOES, r["id"])
            self.assertTrue(r.get("motivo"), r["id"])

    def test_v_a_r_trazem_os_12_com_status(self):
        for r in self.itens:
            if r["decisao"] in ("V", "A", "R"):
                self.assertEqual(set(r["dados"]), set(PO.ITENS), r["id"])
                for k, v in r["dados"].items():
                    self.assertIn(v["status"], PO.STATUS, f"{r['id']}:{k}")
                    if v["status"] == "confirmado":
                        self.assertTrue(v.get("valor"), f"{r['id']}:{k} confirmado sem valor")

    def test_fonte_oficial_nunca_e_agregador_ou_diario(self):
        for r in self.itens:
            f = (r.get("fonte_oficial") or "").lower()
            if r["decisao"] in ("V", "A", "R") and f:
                self.assertFalse(any(p in f for p in PROIBIDAS), f"{r['id']}: {f}")

    def test_nenhuma_data_sem_fonte(self):
        for r in self.itens:
            if r.get("prazo") or r.get("inicio"):
                self.assertTrue(r.get("fonte_oficial"), f"{r['id']}: data sem fonte oficial")

    def test_vigente_nao_tem_prazo_vencido_na_data_da_pesquisa(self):
        for r in self.itens:
            if r["decisao"] == "V" and r.get("prazo"):
                self.assertGreaterEqual(r["prazo"], self.d["data"], r["id"])


class TestTexto(unittest.TestCase):
    def test_conversao(self):
        self.assertEqual(PO.texto_item({"valor": "R$ 10 mil", "status": "confirmado"}), "R$ 10 mil")
        self.assertEqual(PO.texto_item({"valor": "fluxo contínuo", "status": "dispensado pelo edital"}), "dispensado pelo edital: fluxo contínuo")
        self.assertEqual(PO.texto_item({"valor": None, "status": "não informado no edital"}), "não informado no edital")
        self.assertIsNone(PO.texto_item({"valor": None, "status": "não localizado"}), "não localizado continua sendo buscado")
        self.assertIsNone(PO.texto_item({"valor": None, "status": "confirmado"}))


class TestAplicacao(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.orig = (PO.PASTA, PO.EST)
        PO.PASTA = self.tmp / "par"; PO.PASTA.mkdir()
        PO.EST = self.tmp / "opressores.json"
        PO.EST.write_text(json.dumps({"ligados": {
            "ok": {"desde": "2026-09-20", "ate": "2026-10-20", "ia": [], "itens": {}},
            "lixo": {"desde": "2026-09-20", "ate": "2026-10-20", "ia": [], "itens": {}},
            "pend": {"desde": "2026-09-20", "ate": "2026-10-20", "ia": [], "itens": {}}},
            "historico": [{"id": "velho", "desligado_em": "2026-09-01"}]}), encoding="utf-8")
        dz = {k: {"valor": "v", "status": "confirmado"} for k in PO.ITENS}
        dz["Prazo de recurso"] = {"valor": "sem recurso", "status": "dispensado pelo edital"}
        dz["Anexos"] = {"valor": None, "status": "não localizado"}
        (PO.PASTA / "parametros_2026-09-29.json").write_text(json.dumps({"data": "2026-09-29", "itens": [
            {"id": "ok", "decisao": "V", "motivo": "aberto", "fonte_oficial": "https://org.br/e", "prazo": "2026-10-30", "dados": dz},
            {"id": "lixo", "decisao": "D", "motivo": "notícia", "dados": {}},
            {"id": "pend", "decisao": "P", "motivo": "site fora do ar", "dados": {}},
            {"id": "velho", "decisao": "A", "motivo": "encerrado", "fonte_oficial": "https://org.br/v", "prazo": "2026-08-01", "dados": dz},
        ]}), encoding="utf-8")

    def tearDown(self):
        PO.PASTA, PO.EST = self.orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_aplica_uma_vez_so(self):
        r1 = PO.aplicar(date(2026, 9, 29))
        self.assertEqual(r1["desligados"], 1)
        self.assertEqual(r1["itens_gravados"], 11, "11 itens fechados; o 'não localizado' fica para a busca")
        self.assertEqual(r1["historico_anotado"], 1)
        est = json.loads(PO.EST.read_text(encoding="utf-8"))
        self.assertNotIn("lixo", est["ligados"])
        self.assertEqual(est["ligados"]["ok"]["itens"]["Prazo de recurso"], "dispensado pelo edital: sem recurso")
        self.assertNotIn("Anexos", est["ligados"]["ok"]["itens"])
        self.assertEqual(est["ligados"]["ok"]["parametros"]["fechados"], 11)
        self.assertEqual(est["ligados"]["pend"]["parametros"]["decisao"], "P")
        self.assertEqual({h["id"] for h in est["historico"] if h.get("parametros")}, {"velho", "lixo"})
        self.assertEqual(PO.dispensados(), {"lixo"})
        r2 = PO.aplicar(date(2026, 9, 29))
        self.assertEqual({k: v for k, v in r2.items() if v and k != "registros"}, {}, f"segunda aplicação mudou algo: {r2}")

    def test_no_catalogo(self):
        ms = [{"id": "ok"}, {"id": "outro"}]
        self.assertEqual(PO.no_catalogo(ms), 1)
        self.assertEqual(ms[0]["parametros"]["doze"]["Valor"]["status"], "confirmado")


class TestLigacao(unittest.TestCase):
    def test_dispensado_nao_religa(self):
        src = (ROOT / "src/opressores.py").read_text(encoding="utf-8")
        self.assertIn("desligados |= _disp()", src)
        src = (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8")
        self.assertIn('x["id"] not in _disp', src)


if __name__ == "__main__":
    unittest.main()
