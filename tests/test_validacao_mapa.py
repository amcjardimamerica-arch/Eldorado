"""Validação individual do mapa (27/09/2026): decisões, regras aprendidas, aplicação idempotente e fluxo limpo."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src import validacao_mapa as VM

ROOT = Path(__file__).resolve().parents[1]
ARQ = ROOT / "dados/oportunidades/validacao_mapa/validacao_2026-09-27.json"


class TestArquivoDeValidacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = json.loads(ARQ.read_text(encoding="utf-8"))
        cls.itens = cls.dados["itens"]

    def test_universo_inteiro_decidido(self):
        self.assertGreaterEqual(len(self.itens), 1022)
        self.assertEqual(len({r["id"] for r in self.itens}), len(self.itens), "id repetido")
        for r in self.itens:
            self.assertIn(r["decisao"], VM.DECISOES)
            self.assertTrue(r.get("motivo"), r["id"])
        self.assertEqual(sum(self.dados["contagem"].values()), len(self.itens))

    def test_nenhuma_data_sem_fonte_oficial(self):
        for r in self.itens:
            if r.get("prazo") or r.get("inicio"):
                self.assertTrue(r.get("fonte_oficial"), f"{r['id']}: data sem fonte oficial")
                self.assertTrue(r.get("origem_fonte"), r["id"])

    def test_fonte_nunca_e_agregador_ou_diario(self):
        proibidas = ("queridodiario", "pncp.gov.br/app", "observatorio3setor", "captadores.org", "bussolasocial",
                     "prosas.com.br", "idis.org.br", "filantropia.ong", "capitaai")
        for r in self.itens:
            f = (r.get("fonte_oficial") or "").lower()
            if f and r["decisao"] in ("valida_aberta", "valida_fora_abrangencia"):
                self.assertFalse(any(p in f for p in proibidas), f"{r['id']}: fonte proibida {f}")

    def test_validas_na_abrangencia_trazem_os_12_dados(self):
        for r in self.itens:
            if r["decisao"] == "valida_aberta":
                self.assertEqual(set((r.get("doze_itens") or {}).keys()), set(VM.ITENS), r["id"])
                for k, v in r["doze_itens"].items():
                    self.assertIn(v["status"], ("confirmado", "não informado no edital", "dispensado pelo edital", "não localizado"))
                    if v["status"] == "confirmado":
                        self.assertTrue(v.get("valor"), f"{r['id']}:{k} confirmado sem valor")

    def test_regra_aprendida_nunca_descarta_item_que_fica(self):
        for r in self.itens:
            if r["decisao"] not in VM.SAEM_DO_MAPA:
                self.assertIsNone(r.get("regra_aprendida"), f"{r['id']} seria dispensado por {r.get('regra_aprendida')}")

    def test_toda_valida_tem_opressor_ou_motivo(self):
        for r in self.itens:
            if r["decisao"].startswith("valida"):
                op = r.get("opressor") or {}
                self.assertTrue(op.get("id") or op.get("acao"), r["id"])


class TestRegrasAprendidas(unittest.TestCase):
    def d(self, titulo, url, fonte="x", evid=None, origem=None):
        return VM.dispensa(origem or f"motor {fonte}", {"titulo": titulo, "url": url, "fonte_id": fonte, "evidencia": evid})

    def test_vaga_blog_agregador_e_pagina_inicial(self):
        self.assertEqual(self.d("Instituto X contrata Especialista em Captação", "https://captadores.org.br/vagas/x")["regra"], "vaga_emprego")
        self.assertEqual(self.d("Como elaborar edital", "https://blog.prosas.com.br/como")["regra"], "blog_ou_contato")
        self.assertEqual(self.d("Petrobras", "https://petrobras.com.br/")["regra"], "pagina_inicial")
        self.assertEqual(self.d("Editais", "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fmapaosc.ipea.gov.br%2Feditais&rut=1")["regra"], "agregador_sem_oportunidade")

    def test_blog_oficial_do_patrocinador_nao_e_dispensado(self):
        self.assertIsNone(self.d("Parque abre inscrições para o edital 2026", "https://blog.bondinho.com.br/parque-abre-inscricoes-edital-2026"))

    def test_lei_com_ano_nao_e_edicao_antiga(self):
        self.assertIsNone(self.d("PREMIO CULTURAL PNAB LEI N 14.399 2022", "https://pncp.gov.br/app/editais/1/2026/2", fonte="pncp"))
        self.assertEqual(self.d("Estão abertas as inscrições para o dia das boas ações 2018", "https://site.org/x")["regra"], "edicao_antiga")

    def test_trecho_de_diario(self):
        t = "Diário Oficial de X (SP) 2026-09-01 — \"chamamento público\""
        r = self.d(t, "https://data.queridodiario.ok.org.br/1/2026-09-01/a.pdf", fonte="querido-diario",
                   evid="ATO DE DECLARAÇÃO DE INEXIGIBILIDADE DE CHAMAMENTO PÚBLICO a favor da entidade Lar")
        self.assertEqual(r["decisao"], "descartada")
        r = self.d(t, "u", fonte="querido-diario", evid="torna público o RESULTADO FINAL do Edital de Chamamento Público nº 01/2026")
        self.assertEqual(r["decisao"], "arquivada")
        self.assertIsNone(self.d(t, "u", fonte="querido-diario", evid="EDITAL DE CHAMAMENTO PÚBLICO Nº 05/2026 destinado à seleção de Organizações da Sociedade Civil"))
        self.assertIsNone(self.d(t, "u", fonte="querido-diario", evid="AVISO DE RESULTADO FINAL E REABERTURA DE PRAZO EDITAL DE CHAMAMENTO PÚBLICO"))

    def test_heranca_nao_vale_para_diario(self):
        idx = {"t:" + VM._nt("Lei Rouanet"): {"id": "a", "decisao": "descartada"}}
        self.assertEqual(VM.herdada({"titulo": "Lei Rouanet", "url": "https://gov.br/x"}, idx)["id"], "a")
        self.assertIsNone(VM.herdada({"titulo": "Diário Oficial de X (SP) 2026-09-01 — y", "url": "u"}, idx))


class TestAplicacaoIdempotente(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.orig = {k: getattr(VM, k) for k in ("PASTA", "ARQUIVADOS", "EXT", "CAT_OPR", "EST_OPR", "PRED")}
        VM.PASTA = self.tmp / "val"; VM.PASTA.mkdir()
        VM.ARQUIVADOS = self.tmp / "arquivados.json"; VM.EXT = self.tmp / "ext"
        VM.CAT_OPR = self.tmp / "motores.json"; VM.EST_OPR = self.tmp / "opressores.json"; VM.PRED = self.tmp / "pred.jsonl"
        VM.CAT_OPR.write_text(json.dumps({"motores": [{"id": "nova-lixo", "tipo": "oportunidade_mapeada", "ativa": True, "programa": "lixo"}]}), encoding="utf-8")
        VM.EST_OPR.write_text(json.dumps({"ligados": {"nova-lixo": {"desde": "2026-09-20", "ate": "2026-10-20", "ia": [], "itens": {}}}}), encoding="utf-8")
        dz = {k: {"valor": "v", "status": "confirmado"} for k in VM.ITENS}
        itens = [
            {"id": "ok1", "titulo": "Edital bom", "decisao": "valida_aberta", "motivo": "aberto", "fonte_oficial": "https://org.br/edital",
             "origem_fonte": "site oficial do patrocinador", "prazo": "2026-10-30", "doze_itens": dz, "validado_em": "2026-09-27", "opressor": {"id": None}},
            {"id": "enc1", "titulo": "Edital encerrado", "decisao": "arquivada_encerrada", "motivo": "fechou", "fonte_oficial": "https://org.br/velho",
             "origem_fonte": "site oficial do órgão", "prazo": "2026-04-17", "validado_em": "2026-09-27", "opressor": {"id": None}},
            {"id": "lixo1", "titulo": "Notícia", "decisao": "descartada", "motivo": "notícia", "validado_em": "2026-09-27", "opressor": {"id": "nova-lixo"}},
        ]
        (VM.PASTA / "validacao_2026-09-27.json").write_text(json.dumps({"itens": itens}), encoding="utf-8")

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(VM, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_aplica_uma_vez_so(self):
        r1 = VM.aplicar(date(2026, 9, 27))
        self.assertEqual(r1["arquivados_novos"], 2)
        self.assertEqual(r1["opressores_criados"], 1)
        self.assertEqual(r1["opressores_desligados"], 1)
        self.assertEqual(r1["preditivo_novo"], 2)
        arq = json.loads(VM.ARQUIVADOS.read_text(encoding="utf-8"))
        self.assertEqual(arq["lixo1"]["estado"], "descartado"); self.assertEqual(arq["enc1"]["estado"], "encerrado")
        est = json.loads(VM.EST_OPR.read_text(encoding="utf-8"))
        self.assertNotIn("nova-lixo", est["ligados"])
        novo = [k for k in est["ligados"] if k != "nova-lixo"][0]
        self.assertEqual(len(est["ligados"][novo]["itens"]), 12, "opressor nasce com os 12 dados confirmados")
        ve = json.loads((VM.EXT / "ok1.json").read_text(encoding="utf-8"))["verificacao_externa"]
        self.assertEqual(ve["prazo"], "2026-10-30")
        pred = [json.loads(l) for l in VM.PRED.read_text(encoding="utf-8").splitlines()]
        enc = [p for p in pred if p["id"] == "enc1"][0]
        self.assertEqual(enc["proxima_janela_estimada"], "2027-04")
        r2 = VM.aplicar(date(2026, 9, 27))
        self.assertEqual({k: v for k, v in r2.items() if v}, {}, f"segunda aplicação mudou algo: {r2}")


class TestFluxoLimpo(unittest.TestCase):
    def test_mapa_so_tem_valida_fora_ou_pendente_entre_os_validados(self):
        from src import fluxo_oportunidades as F
        V = VM.carregar()
        for x in F.consolidar():
            v = V.get(x["id"])
            if v:
                self.assertNotIn(v["decisao"], VM.SAEM_DO_MAPA, x["id"])
            if v and v["decisao"] == "pendente":
                self.assertFalse(x["confirmada"], f"{x['id']} pendente não pode aparecer confirmada")


if __name__ == "__main__":
    unittest.main()
