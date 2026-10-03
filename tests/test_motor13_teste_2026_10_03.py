"""03/10/2026 — teste do motor 13 (25 prefeituras de GO): edição do Querido Diário não é seleção aberta, título genérico
decidido pelo resumo, status 'falhou' visível, publicado × lido por cidade/rota (paginas_nao_lidas e aguardando_brasil). Sem rede."""
import json, sys, time, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import prefeituras_25_go as P
from src import maestro

H = date(2026, 10, 3)
LEX = P.config()["lexico"]


class Classificador(unittest.TestCase):
    def test_titulo_generico_com_prorrogacao(self):
        k = P.classificar("EDITAL Nº 01/2025", "COMUNICADO DE PRORROGAÇÃO — renovação de instituições/ONGs vinculadas aos conselhos CMAS, CMDCA "
                          "e CMDPI; prorrogação por 30 dias do prazo de divulgação do resultado", date(2026, 9, 11), H, LEX)
        self.assertEqual((k["veredito"], k["categoria"]), ("ACOMPANHAR", "ATO_DO_EDITAL"))

    def test_edital_de_ano_anterior_publicado_de_novo(self):
        k = P.classificar("EDITAL Nº 07/2025", "instituições sem fins lucrativos", date(2026, 9, 11), H, LEX)
        self.assertEqual(k["categoria"], "ATO_DO_EDITAL")

    def test_abertura_verdadeira_continua(self):
        k = P.classificar("EDITAL Nº 03/2026", "Abre inscrições para organizações da sociedade civil, termo de fomento, inscrições até 30/10/2026",
                          date(2026, 9, 20), H, LEX)
        self.assertEqual((k["veredito"], k["aberta"], k["prazo"]), ("OPORTUNIDADE", True, "2026-10-30"))

    def test_trecho_com_reticencias_e_extrato(self):
        t = "... Extrato do Termo de Fomento nº 12/2026 celebrado com a Associação X, decorrente de chamamento público ..."
        self.assertEqual(P.classificar(t[:300], t, date(2026, 9, 30), H, LEX)["categoria"], "PARCERIA_DIRETA")


class QueridoDiario(unittest.TestCase):
    def _cidade(self, trecho):
        cfg = P.config()
        m = {"municipio": "Goiânia", "site": "https://www.goiania.go.gov.br", "qd": "5208707", "ibge": "5208707"}
        pub = P._pub("Goiânia", "Querido Diário", "https://data.queridodiario.org.br/x.pdf",
                     "Diário Oficial de Goiânia — edição 8874 (2026-09-30) — chamamento público", "2026-09-30", trecho)
        with mock.patch.object(P, "_rotas", return_value=["qd"]), mock.patch.object(P, "_ler_rota", return_value=("lida", [pub], {})):
            return P.processar_cidade({"municipio": "Goiânia", "camada": 4}, m, cfg, H, time.time() + 60)

    def test_edicao_com_o_termo_nao_e_aberta(self):
        ab, passadas = self._cidade("… resultado do chamamento público para organizações da sociedade civil …")
        self.assertEqual(ab, [])

    def test_edicao_sem_prazo_nao_e_aberta(self):
        ab, passadas = self._cidade("… edital de chamamento público para organizações da sociedade civil, termo de colaboração …")
        self.assertEqual(ab, []); self.assertEqual(len(passadas), 1)
        self.assertIn("sem prazo", passadas[0]["motivo"])

    def test_edicao_com_prazo_e_aberta(self):
        ab, _ = self._cidade("… edital de chamamento público para organizações da sociedade civil, inscrições até 20/10/2026 …")
        self.assertEqual(len(ab), 1)


class StatusECobertura(unittest.TestCase):
    def test_falha_aparece_mesmo_com_rota_do_brasil(self):
        cfg = P.config()
        m = next(x for x in cfg["municipios"] if x["municipio"] == "Inhumas")
        c = {"municipio": "Inhumas", "camada": 4}
        def rota(r, *a, **k):
            return ("falhou", [], {}) if r == "agm" else ("aguardando coleta local (Brasil)", [], {})
        with mock.patch.object(P, "_ler_rota", side_effect=rota):
            P.processar_cidade(c, m, cfg, H, time.time() + 60)
        self.assertEqual(c["status"], "falhou")

    def test_maestro_brasil_e_nuvem(self):
        reg = {"cor": "azul", "falhas": 0}
        self.assertEqual(maestro.cobertura(P.MOTOR_ID, reg, {}, {"aguardando_brasil": ["Anápolis · wp"]}), "pendente_local")
        self.assertEqual(maestro.cobertura(P.MOTOR_ID, reg, {}, {"paginas_nao_lidas": ["Inhumas · agm: falhou"], "aguardando_brasil": ["x"]}),
                         "parcial")
        self.assertEqual(maestro.cobertura(P.MOTOR_ID, reg, {}, {}), "completa")

    def test_ler_motor_marca_o_que_falta(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        def rota(r, m, *a, **k):
            if r == "agm" and m["municipio"] == "Inhumas":
                return ("falhou", [], {})
            return ("aguardando coleta local (Brasil)", [], {}) if r in ("wp", "portal") else ("vazia", [], {})
        with mock.patch.object(P, "ESTADO", d / "e.json"), mock.patch.object(P, "_ler_rota", side_effect=rota), \
             mock.patch.object(P, "_livros"), mock.patch.object(P, "painel"):
            r = P.ler_motor(hoje=H)
        dg = r["diagnostico"]
        self.assertIn("Inhumas · agm: falhou", dg["paginas_nao_lidas"])
        self.assertTrue(dg["aguardando_brasil"]); self.assertTrue(dg["exige_brasil"])
        self.assertEqual(dg["leitura_do_dia"]["falharam"], 1)

    def test_senador_canedo_sem_rota_agm(self):
        m = next(x for x in P.config()["municipios"] if x["municipio"] == "Senador Canedo")
        self.assertNotIn("agm", m); self.assertIn("nota_agm", m)


if __name__ == "__main__":
    unittest.main()
