"""02/10/2026 (titular): reorganização dos motores — indexadores desmontados em motores por site, leitura a partir da
última leitura (lacuna → mais páginas), registro compacto, motor criado quando falta, Judiciário (TJ-GO/CNJ) e MP
(MP-GO/MPT-GO/MPU) separados, incentivos unificados, Prefeituras das 25 e a ordem do painel."""
import json, sys, unittest
from datetime import date, datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.indexadores import motor as IM

J = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))   # noqa: E731


class TesteDesmonte(unittest.TestCase):
    def test_um_motor_por_site_sem_familias(self):
        C = J("config/indexadores.json")
        self.assertFalse([m for m in C["motores"] if m.startswith("idx-")])
        AG = (C.get("agregados") or {}).get("motores") or {}       # 03/10 (titular): sites agregados ao motor 20 e ao 17
        for s in C["sites"]:
            self.assertIn(s["motor"], set(C["motores"]) | set(AG), s["id"])
        for mid, m in C["motores"].items():
            self.assertTrue(m.get("local") and m.get("finalidade") and m.get("fonte") is not None, mid)
            self.assertTrue(m["nome"].startswith(m["local"]), mid)                   # o nome começa pelo local de busca
        desc = {d["id"] for d in C["descartados"] if isinstance(d, dict) and d.get("em") == "2026-10-02"}
        self.assertEqual(desc, {"salic-minc", "gife-capta", "fapeg-secult", "radar-portal-impacto", "fundsforngos-brasil"})
        self.assertIn("site-mapa-osc", C["motores"]); self.assertIn("site-prosas", C["motores"])   # correções da implantação
        self.assertEqual(len(next(s for s in C["sites"] if s["id"] == "prosas").get("caminhos_indiretos") or []), 3)

    def test_lacuna_puxa_mais_paginas_e_registro_compacto(self):
        st = {}
        agora = datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)
        res = {"itens": [{"chave": "a", "publicado": "2026-10-02"}, {"chave": "b", "publicado": "2026-10-03"}], "lidas": 2}
        r = IM.registrar_leitura(st, res, {"paginas_retroativas": 2}, "2026-09-25", 0, agora)
        self.assertTrue(r["lacuna"]); self.assertEqual(st["paginas_extra"], 1)                 # não chegou a 25/09 e esgotou as páginas
        self.assertEqual((r["de"], r["ate"], r["n"]), ("2026-10-02", "2026-10-03", 2)); self.assertEqual(len(r["h"]), 12)
        res2 = {"itens": [{"chave": "c", "publicado": "2026-09-20"}], "lidas": 3}
        r2 = IM.registrar_leitura(st, res2, {"paginas_retroativas": 3}, "2026-09-25", 1, agora)
        self.assertFalse(r2["lacuna"]); self.assertEqual(st["paginas_extra"], 0)              # fechou o buraco
        for _ in range(40):
            IM.registrar_leitura(st, res2, {"paginas_retroativas": 3}, None, 0, agora)
        self.assertEqual(len(st["leituras"]), 30)                                              # economia: só as 30 últimas

    def test_motor_criado_quando_falta_e_instancia_alimenta_existente(self):
        cat = {"sites": [{"id": "x", "url": "https://coberto.org.br/editais", "instancias": [{"host": "mapa.cultura.go.gov.br"}]}], "descartados": []}
        it = lambda u, perfil="osc": {"link_oficial": u, "perfil": perfil, "pais": "BR"}   # noqa: E731
        ac = {"itens": {str(i): v for i, v in enumerate([
            it("https://fonte-nova.org.br/editais/2026/edital-1"), it("https://fonte-nova.org.br/editais/2026/edital-2"),
            it("https://mapa.cultura.xx.gov.br/oportunidade/1/"), it("https://mapa.cultura.xx.gov.br/oportunidade/2/"),
            it("https://coberto.org.br/editais/9"), it("https://coberto.org.br/editais/10"),
            {**it("https://estrangeiro.com/call/1"), "pais": None}, {**it("https://estrangeiro.com/call/2"), "pais": None},
            it("https://naoaplica.org.br/a/1", "fora"), it("https://naoaplica.org.br/a/2", "fora")])}}
        from unittest import mock
        with mock.patch("src.indexacao_livros.mapa_dominios", lambda: {}):
            out = {m["nome"]: m for m in IM.motores_que_faltam(ac, cat)}
        self.assertEqual(set(out), {"fonte-nova.org.br", "mapa.cultura.xx.gov.br"})
        self.assertEqual(out["fonte-nova.org.br"]["listas"], ["https://fonte-nova.org.br/editais/2026/"])
        self.assertEqual(out["mapa.cultura.xx.gov.br"]["tipo"], "instancia_mapas_culturais")


class TesteSeparacoes(unittest.TestCase):
    def test_judiciario_em_duas_partes(self):
        from src import judiciario_go as JG
        self.assertEqual(JG.PARTES["judiciario-tjgo"][0], "ABDE"); self.assertEqual(JG.PARTES["judiciario-cnj"][0], "C")
        JG._PARTE.update(id="judiciario-cnj", fontes="C")
        try:
            self.assertEqual(JG.fonte_a(date(2026, 10, 2), {}, {"fontes": {"A": {"falhas": [], "consultas": 0, "itens": 0}}}, {}), [])
            self.assertIsNone(JG.habilitacao_previa({}))
        finally:
            JG._PARTE.update(id=None, fontes="ABCDE")
        S = {s["id"]: s for s in J("config/sensores.json")["sensores_especiais"]}
        self.assertTrue(all("tjgo" in u for u in S["judiciario-tjgo"]["urls"])); self.assertTrue(all("cnj" in u for u in S["judiciario-cnj"]["urls"]))

    def test_mp_em_tres_partes(self):
        from src import ministerios_publicos as MP
        for mid, org, sim in (("mpgo-destinacao", "MP-GO", True), ("mpgo-destinacao", "MPF", False), ("mptgo-destinacao", "MPT-GO", True),
                              ("mpu-destinacao", "MPF", True), ("mpu-destinacao", "MPT-GO", False), ("mpu-destinacao", "MPT nacional", True)):
            MP._PARTE["id"] = mid
            try:
                self.assertEqual(MP._da_parte(org), sim, (mid, org))
            finally:
                MP._PARTE["id"] = None
        self.assertTrue(MP.selecao_sem_edital("Não há seleção em andamento")); self.assertFalse(MP.selecao_sem_edital("Seleção em andamento: Edital 1/2027"))

    def test_agregados_fora_do_painel_e_incentivos_unificados(self):
        A = J("config/agenda_motores.json")["motores"]
        for velho, novo in (("judiciario-cnj-tjgo", "judiciario-tjgo"), ("empresas-incentivadas", "motor-gife")):
            self.assertEqual((A[velho]["dias"], A[velho]["agregado_a"]), ("inativo", novo))
        self.assertIn("MOTORES_FONTES=empresas-incentivadas", (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8"))


class TesteOrdemENomes(unittest.TestCase):
    def test_ordem_do_titular(self):
        P = J("config/ordem_motores.json")["posicoes"]
        esperado = ["do-goiania", "do-goias", "dou", "camara-goiania-pl", "alego-pl", "congresso-nacional", "judiciario-tjgo", "mpgo-destinacao",
                    "mptgo-destinacao", "mpu-destinacao", "judiciario-cnj", "dj-trf1-go", "prefeituras-50-go", "estaduais-go-gov", "pncp-api", "salic",
                    "cnpq-extensao", "gife", "empresas-editais-incentivados", "motor-gife", "motor-patrocinio", "piloto-aberto", "piloto-interceptador"]
        self.assertEqual([k for k, _ in sorted(P.items(), key=lambda kv: kv[1])][:23], esperado)
        self.assertTrue(all(k.startswith("site-") for k, v in P.items() if v >= 24))

    def test_nomes(self):
        I = {f["id"]: f for f in J("config/investigacao.json")["fontes"]}
        self.assertIn("25 maiores cidades", I["prefeituras-50-go"]["nome"])
        self.assertTrue(I["empresas-editais-incentivados"]["nome"].startswith("Busca de empresas para FIA, Idoso"))



class TesteAgregacao0310(unittest.TestCase):
    """03/10/2026 (titular): motores 40, 41, 43, 44, 45 e 47 agregados ao 20; motor 42 agregado ao 17."""
    AO_20 = {"embaixadas": "site-embaixada-japao", "embaixada-eua": "site-embaixada-eua", "fbb": "site-fundacao-banco-do-brasil",
             "iaf": "site-iaf", "itau-social": "site-itau-social", "petrobras": "site-petrobras"}

    def test_sites_agregados_e_lidos(self):
        C = J("config/indexadores.json"); S = {s["id"]: s for s in C["sites"]}; AG = C["agregados"]["motores"]
        for sid, antigo in self.AO_20.items():
            self.assertEqual((S[sid]["motor"], S[sid]["motor_antigo"]), ("motor-gife", antigo))
            self.assertNotIn(antigo, C["motores"])
        self.assertEqual({a["site"] for a in AG["motor-gife"]}, set(self.AO_20))
        self.assertEqual((S["finep"]["motor"], [a["site"] for a in AG["plat-cnpq-extensao"]]), ("plat-cnpq-extensao", ["finep"]))
        self.assertNotIn("site-finep", C["motores"])

    def test_ordem_agenda_e_rotas(self):
        P = J("config/ordem_motores.json")["posicoes"]
        self.assertEqual(len(P), 42); self.assertEqual(sorted(P.values()), list(range(1, 43)))
        self.assertEqual((P["cnpq-extensao"], P["motor-gife"], P["site-mapa-osc"], P["site-prosas"], P["site-rede-filantropia"]), (17, 20, 40, 41, 42))
        A = J("config/agenda_motores.json")["motores"]
        for antigo in list(self.AO_20.values()) + ["site-finep"]:
            self.assertNotIn(antigo, P)
            self.assertEqual(A[antigo]["dias"], "inativo")
            self.assertEqual(A[antigo]["agregado_a"], "cnpq-extensao" if antigo == "site-finep" else "motor-gife")
        R = J("config/rotas_motores.json")["motores"]
        self.assertEqual(len(R["motor-gife"]["rotas_agregadas"]), 6)
        self.assertEqual(len(R["plat-cnpq-extensao"]["rotas_agregadas"]), 1)
        # o sensor do motor NÃO lê as rotas agregadas (a Finep proíbe robôs): elas ficam fora de 'rotas'
        self.assertFalse([r for r in R["plat-cnpq-extensao"]["rotas"] if "finep" in str(r.get("url"))])


if __name__ == "__main__":
    unittest.main()
