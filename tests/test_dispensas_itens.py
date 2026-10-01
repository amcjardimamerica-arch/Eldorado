"""Dispensa dos 12 itens por tipo de recurso (01/10/2026): matriz, regime, checklist e parâmetros de 01/10."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from src import dispensas_itens as DI
from src import parametros_opressores as PO

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "dados/opressores/parametros/parametros_2026-10-01.json"
PROIBIDAS = ("queridodiario", "pncp.gov.br/app", "observatorio3setor", "captadores.org", "bussolasocial",
             "prosas.com.br", "idis.org.br", "filantropia.ong", "capitaai", "farolcultural", "duckduckgo")


class TestMatriz(unittest.TestCase):
    def test_itens_so_dos_12_e_situacao_valida(self):
        M = DI.matriz()
        self.assertIn(DI.PADRAO, M["regimes"])
        for rid, R in M["regimes"].items():
            for k, v in R["itens"].items():
                self.assertIn(k, DI.ITENS, f"{rid}:{k}")
                self.assertIn(v["situacao"], ("dispensa_provavel", "nao_se_aplica"), f"{rid}:{k}")
                self.assertTrue(v.get("porque") and v.get("base") and v.get("confianca"), f"{rid}:{k} sem porquê/base/confiança")

    def test_edital_padrao_nao_dispensa_nada(self):
        self.assertEqual(DI.matriz()["regimes"][DI.PADRAO]["itens"], {})
        self.assertEqual(DI.analisar(DI.PADRAO)["provaveis"], {})

    def test_bases_verificadas_tem_url_oficial(self):
        for k, b in DI.matriz()["bases_verificadas"].items():
            self.assertTrue(b["url"].startswith("https://www.planalto.gov.br/"), k)
            self.assertEqual(b["verificado_em"], "2026-10-01")


class TestRegime(unittest.TestCase):
    def test_emenda_e_fluxo(self):
        self.assertEqual(DI.regime(None, "x", emenda=True)[0], "emenda_parlamentar")
        self.assertEqual(DI.regime(None, "x", prazo_dispensado=True)[0], "fluxo_continuo")

    def test_catalogo_tem_prioridade_sobre_titulo(self):
        self.assertEqual(DI.regime({"tipo_objeto": "Incentivo fiscal"}, "chamamento público")[0], "incentivo_fiscal")
        self.assertEqual(DI.regime({"regime_inscricao": "contínuo"}, "edital")[0], "fluxo_continuo")

    def test_titulo_e_padrao(self):
        self.assertEqual(DI.regime(None, "Edital de chamamento público 01/2026")[0], DI.PADRAO)
        self.assertEqual(DI.regime(None, "Credenciamento em fluxo contínuo nº 001/2026")[0], "fluxo_continuo")
        self.assertEqual(DI.regime(None, "Doação de mercadorias apreendidas")[0], "doacao_de_bens")
        self.assertEqual(DI.regime(None, "Edital", privada=True)[0], "patrocinio_privado")


class TestChecklist(unittest.TestCase):
    def _ck(self, **o):
        ck = {k: {"s": "falta"} for k in DI.ITENS}
        for k, s in o.items():
            ck[k.replace("_", " ")] = {"s": s}
        return ck

    def test_prov_so_onde_falta_e_o_regime_dispensa(self):
        ck = self._ck(Valor="ok")
        r = DI.aplicar_ao_checklist(ck, "emenda_parlamentar")
        self.assertEqual(ck["Valor"]["s"], "ok", "item já comprovado não vira provável")
        self.assertEqual(ck["Resultado"]["s"], "prov")
        self.assertEqual(ck["Objeto"]["s"], "falta", "o regime exige o objeto")
        self.assertNotIn("Valor", r["provaveis"])
        self.assertIn("Objeto", r["exigidos_em_aberto"])

    def test_confirmado_pelo_edital_prevalece_sobre_provavel(self):
        ck = self._ck(Prazo_de_inscrição="disp")
        DI.aplicar_ao_checklist(ck, "fluxo_continuo")
        self.assertEqual(ck["Prazo de inscrição"]["s"], "disp")

    def test_prov_traz_motivo_base_e_confianca(self):
        ck = self._ck()
        DI.aplicar_ao_checklist(ck, "patrocinio_privado")
        self.assertEqual(ck["Prazo de recurso"]["s"], "prov")
        self.assertTrue(ck["Prazo de recurso"]["v"] and ck["Prazo de recurso"]["t"] and ck["Prazo de recurso"]["c"])

    def test_livro_anota_so_nao_localizado(self):
        par = {"doze": {k: {"valor": None, "status": "não localizado"} for k in DI.ITENS}}
        par["doze"]["Prazo de recurso"] = {"valor": "5 dias úteis", "status": "confirmado"}
        DI.no_livro(par, {"natureza": "privada", "tipo": "grant"}, "")
        self.assertEqual(par["regime"]["id"], "patrocinio_privado")
        self.assertNotIn("dispensa_provavel", par["doze"]["Prazo de recurso"], "o que o edital trouxe não é dispensa")
        par["doze"]["Prazo de recurso"] = {"valor": None, "status": "não localizado"}
        DI.no_livro(par, {"natureza": "privada", "tipo": "grant"}, "")
        self.assertIn("dispensa_provavel", par["doze"]["Prazo de recurso"])
        self.assertNotIn("Prazo de recurso", par["faltam_exigidos"])
        self.assertIn("Objeto", par["faltam_exigidos"])
        self.assertEqual(PO.texto_item(par["doze"]["Prazo de recurso"]), None, "provável não vira texto de item fechado")


class TestLivroVerificadoPorOutraVia(unittest.TestCase):
    def test_livro_fora_do_arquivo_de_parametros_ganha_a_analise_e_fica_estavel(self):
        import shutil
        import tempfile
        tmp = Path(tempfile.mkdtemp()); orig = (PO.PASTA, PO.EST)
        try:
            PO.PASTA = tmp / "par"; PO.PASTA.mkdir(); PO.EST = tmp / "livros.json"
            doze = {k: {"valor": "v", "status": "confirmado"} for k in DI.ITENS}
            doze["Prazo de recurso"] = {"valor": None, "status": "não localizado"}
            PO.EST.write_text(json.dumps({"ligados": {"x": {"itens": {}, "parametros": {"decisao": "V", "doze": doze}}}, "historico": []}), encoding="utf-8")
            r1 = PO.aplicar(); self.assertEqual(r1["opressores_atualizados"], 1)
            par = json.loads(PO.EST.read_text(encoding="utf-8"))["ligados"]["x"]["parametros"]
            self.assertIn("regime", par); self.assertEqual(par["faltam_exigidos"], ["Prazo de recurso"])
            self.assertEqual(PO.aplicar()["opressores_atualizados"], 0, "segunda aplicação não muda nada")
        finally:
            PO.PASTA, PO.EST = orig; shutil.rmtree(tmp, ignore_errors=True)


class TestFluxoLigado(unittest.TestCase):
    def test_checklist_usa_doze_itens_e_parametros(self):
        src = (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8")
        self.assertIn('_vv.get("doze_itens")', src)
        self.assertIn('_pdz = _par.get("doze")', src)
        self.assertIn("aplicar_ao_checklist", src)

    def test_saida_nao_conta_prov_nem_ref_como_feito(self):
        html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('feitos=n("ok")+n("disp")+n("val")', html)
        self.assertIn("prov:", html)


class TestParametros1001(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(ARQ.read_text(encoding="utf-8"))
        cls.itens = cls.d["itens"]

    def test_composicao(self):
        c = self.d["composicao"]
        self.assertEqual(c["novos"], 79)
        self.assertEqual(c["completados"], 57)
        self.assertEqual(len(self.itens), c["novos"] + c["completados"] + c["v_para_a_por_prazo_vencido_na_base"])
        self.assertEqual(sum(self.d["contagem"].values()), len(self.itens))
        self.assertEqual(len({r["id"] for r in self.itens}), len(self.itens))

    def test_regras_do_titular(self):
        for r in self.itens:
            self.assertIn(r["decisao"], PO.DECISOES, r["id"])
            self.assertFalse(r.get("injecao"), r["id"])
            f = (r.get("fonte_oficial") or "").lower()
            self.assertFalse(any(p in f for p in PROIBIDAS), f"{r['id']}: {f}")
            if r.get("prazo") or r.get("inicio"):
                self.assertTrue(r.get("fonte_oficial"), f"{r['id']}: data sem fonte oficial")
            if r["decisao"] in ("V", "A", "R"):
                self.assertEqual(set(r["dados"]), set(PO.ITENS), r["id"])
                for k, v in r["dados"].items():
                    self.assertIn(v["status"], PO.STATUS, f"{r['id']}:{k}")
                    if v["status"] == "confirmado":
                        self.assertTrue(v.get("valor"), f"{r['id']}:{k} confirmado sem valor")

    def test_vigente_nao_tem_prazo_vencido(self):
        for r in self.itens:
            if r["decisao"] == "V" and r.get("prazo"):
                self.assertGreaterEqual(r["prazo"], self.d["data"], r["id"])

    def test_completados_nao_perdem_o_que_ja_estava_fechado(self):
        ant = {r["id"]: r for r in json.loads((ROOT / "dados/opressores/parametros/parametros_2026-09-29.json").read_text(encoding="utf-8"))["itens"]}
        for r in self.itens:
            a = ant.get(r.get("id_pesquisado") or r["id"])
            if r.get("completado_em") and a:
                for k, v in (a.get("dados") or {}).items():
                    if v["status"] != "não localizado":
                        self.assertEqual(r["dados"][k]["status"], v["status"], f"{r['id']}:{k} regrediu")

    def test_carregar_usa_o_mais_recente(self):
        P = PO.carregar()
        for r in self.itens:
            self.assertEqual(P[r["id"]]["decisao"], r["decisao"], r["id"])


if __name__ == "__main__":
    unittest.main()
