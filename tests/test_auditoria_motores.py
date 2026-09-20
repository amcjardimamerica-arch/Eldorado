"""Auditoria dos motores de 20/09/2026 — reestruturação e parecer do conselho."""
import datetime
import json
import os
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteReestruturacaoDosMotores(unittest.TestCase):
    def test_regulares_nunca_sao_cortados_pelo_limite(self):
        """As 4 plataformas ficaram 14 dias sem rodar porque a ordenação 'Goiás primeiro'
        as empurrava para o fim e o corte de 40 as deixava de fora."""
        os.environ["GITHUB_ACTIONS"] = "true"
        from src.sensores import escala_do_dia, registro
        for d in range(7):
            e = escala_do_dia(datetime.date(2026, 9, 14) + datetime.timedelta(days=d))
            regulares = [s for s in registro() if not s.get("fontes_260")]
            ids_saem = {s["id"] for s in e["saem"]}
            plataformas = {s["id"] for s in regulares if s["tipo"] == "plataforma"}
            self.assertTrue(plataformas <= ids_saem, f"plataformas fora da escala no dia {d}: {plataformas - ids_saem}")
            self.assertIn("regulares_garantidos", e)
            self.assertLessEqual(len(e["saem"]), 40)

    def test_toda_plataforma_configurada_vira_sensor(self):
        """Prosas, SALIC e Secult-GO nunca tinham rodado: descartadas por deduplicação de URL."""
        from src.sensores import registro
        inv = json.loads((ROOT / "config/investigacao.json").read_text(encoding="utf-8"))
        ativas = {f"plat-{f['id']}" for f in inv["fontes"] if f.get("ativa", True)}
        ids = {s["id"] for s in registro()}
        self.assertTrue(ativas <= ids, f"plataformas sem sensor: {ativas - ids}")
        for pid in ("plat-prosas", "plat-salic", "plat-secult-go"):
            self.assertIn(pid, ids)
        self.assertNotIn("plat-mapa-osc", ids)                      # desativado com motivo

    def test_motores_novos_do_radar(self):
        inv = json.loads((ROOT / "config/investigacao.json").read_text(encoding="utf-8"))
        ids = {f["id"] for f in inv["fontes"]}
        for novo in ("ovg", "goias-social", "fundos-estaduais-go", "fapeg", "prefeituras-50-go",
                     "empresas-editais-incentivados", "mp-destinacoes-reparacao", "cnpq-extensao"):
            self.assertIn(novo, ids, novo)
        ovg = [f for f in inv["fontes"] if f["id"] == "ovg"][0]
        self.assertIn("ovg.org.br", ovg["url"]); self.assertTrue(ovg.get("o_que_procurar"))

    def test_auditoria_classifica_e_da_parecer(self):
        from src.auditoria_motores import _estado, CONSELHO, CADENCIA
        hoje = datetime.date(2026, 9, 20)
        self.assertEqual(_estado({}, hoje)[0], "NUNCA RODOU")
        self.assertEqual(_estado({"ultima": "2026-09-06T00:00:00", "achados_total": 23}, hoje)[0], "PARADO")
        self.assertEqual(_estado({"ultima": "2026-09-20T00:00:00", "achados_total": 0}, hoje)[0], "LENDO SEM ACHAR")
        self.assertEqual(_estado({"ultima": "2026-09-20T00:00:00", "achados_total": 2}, hoje)[0], "FUNCIONANDO")
        self.assertEqual(_estado({"ultima": "2026-09-20T00:00:00", "saude": [{"erro": "HTTPError"}]}, hoje)[0], "BLOQUEADO")
        self.assertEqual(CADENCIA, 7)
        for k, v in CONSELHO.items():
            self.assertTrue(v.get("pess") and v.get("otim") and v.get("decide"), k)
        a = json.loads((ROOT / "estado/auditoria_motores.json").read_text(encoding="utf-8"))
        self.assertEqual(a["total"], sum(a["por_estado"].values()))
        self.assertTrue(all(x["conselho"].get("neutro_decide") for x in a["itens"]))
        self.assertGreaterEqual(len(a["correcoes_de_hoje"]), 3)
        d = json.loads((ROOT / "docs/dashboard-dados.json").read_text(encoding="utf-8"))
        self.assertIn("auditoria_motores", d)
        self.assertIn("Auditoria dos motores", (ROOT / "docs/dashboard.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
