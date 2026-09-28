"""Guardas contra o que a tela não mostra (27/09)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TesteIntegridadePainel(unittest.TestCase):
    def test_gerador_nao_reescreve_o_painel(self):
        """Às 21h49 de 27/09 um voo regravou docs/dashboard.html com a cópia antiga e desfez a leitura pela API."""
        src = (ROOT / "src/dashboard_dados.py").read_text(encoding="utf-8")
        self.assertNotIn("html.write_text(t2", src)

    def test_leitura_ao_vivo_pela_api_e_reservas(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for trecho in ("REPO_API+cam", "REPO_RAW+cam", "_ETAG[cam]", "atualizarAgora", "seloVivo", "window._SAUDE"):
            self.assertIn(trecho, h, trecho)

    def test_fragmentos_grandes_so_regravados_se_mudarem(self):
        src = (ROOT / "src/dashboard_dados.py").read_text(encoding="utf-8")
        for nome in ("abertas.json", "historico.json", "previsoes.json", "empresas.json"):
            self.assertRegex(src, r'_grava_se_mudou\(pasta / "' + re.escape(nome) + '"')

    def test_prontidao_nao_roda_a_cada_gravacao_dos_pilotos(self):
        y = (ROOT / ".github/workflows/00-prontidao.yml").read_text(encoding="utf-8")
        self.assertNotIn("on: [workflow_dispatch, push]", y)
        self.assertIn("paths:", y)

    def test_saude_publicada_e_valida(self):
        from src.saude import checar
        r = checar()
        self.assertIn("alertas", r); self.assertIn("ok", r)
        json.loads((ROOT / "docs/dados/saude.json").read_text(encoding="utf-8"))

    def test_catalogo_de_opressores_sem_duplicados(self):
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8")).get("motores", [])
        ch = [re.sub(r"[^a-z0-9]", "", f"{x.get('programa')}{x.get('orgao')}".lower())[:80] for x in C]
        self.assertEqual(len(ch), len(set(ch)))

    def test_mapa_so_com_validacao(self):
        """28/09: um voo com código antigo publicou o mapa sem a validação (11/1018) por 10 minutos."""
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        self.assertTrue((F.get("validacao") or {}).get("aplicada"))
        self.assertEqual((F.get("validacao") or {}).get("sem_decisao"), 0)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("eldorado_fluxo_valido", h); self.assertIn("_FLUXO_RECUSADO", h)
        for w in ("monitoramento-diario.yml", "interceptador.yml"):
            self.assertIn("fluxo_oportunidades --completo", (ROOT / ".github/workflows" / w).read_text(encoding="utf-8"))

    def test_curadoria_decide_o_que_nao_serve(self):
        from src.curadoria_automatica import decidir
        self.assertEqual(decidir({"titulo": "Fundo Patrimonial FEAUSP", "tipo": "empresa/instituto"})["decisao"], "descartada")
        self.assertEqual(decidir({"titulo": "Editalagua2022", "url": "https://x.org/edital-2022"})["decisao"], "arquivada_encerrada")
        self.assertIsNone(decidir({"titulo": "Edital X", "confirmada": True}))

    def test_quadro_de_novas_respeita_a_validacao(self):
        """28/09: o quadro 'novas oportunidades anunciadas' mostrava 7 itens já descartados ou encerrados."""
        from src.validacao_mapa import carregar, SAEM_DO_MAPA
        V = carregar()
        saem = {v.get("titulo") for v in V.values() if v.get("decisao") in SAEM_DO_MAPA}
        novas = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8")).get("novas") or []
        self.assertFalse([n["titulo"] for n in novas if n.get("titulo") in saem and not any(
            v.get("titulo") == n["titulo"] and v.get("decisao") not in SAEM_DO_MAPA for v in V.values())])

    def test_calendario_inicial_so_com_data(self):
        """28/09: o calendário da página inicial mostrava edital sem data ('marcado para a IA')."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("CALENDÁRIO DE EDITAIS DA PÁGINA INICIAL (titular, 28/09)", h)
        novo = h[h.index("CALENDÁRIO DE EDITAIS DA PÁGINA INICIAL (titular, 28/09)"):h.index("function ddmmG(")]
        self.assertNotIn("marcado para a IA", novo.split("*/", 1)[1])
        self.assertIn("F.calendario", novo)

    def test_regra_maxima(self):
        """28/09: nenhuma caixa estática — dados ao vivo, código ao vivo, publicação contínua, selo em cada caixa."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("window.conferirVersaoDoPainel=", h)
        passos = h[h.index("window.atualizarAgora=async function"):h.index("setInterval(()=>atualizarAgora(),240000)")]
        for f in ("desenhaGantt", "desenhaCal", "desenhaEditais", "desenhaBzMapa", "desenhaMotores", "desenhaApoiadores",
                  "desenhaPostoPiloto", "desenhaPostoInterceptador", "carregaFluxo"):
            self.assertIn(f, passos, f"caixa sem atualização contínua: {f}")
        selos = h[h.index("const SELOS=["):h.index("function pintarSelos")]
        for el in ("g-corpo", "cal-grade", "bz-mapa", "mt-lista", "rank-apoiadores", "int-posto", "ed-grade"):
            self.assertIn(f'"{el}"', selos, f"caixa sem selo de procedência: {el}")
        y = (ROOT / ".github/workflows/publicar-painel.yml").read_text(encoding="utf-8")
        self.assertIn("docs/dashboard.html", y)
        json.loads((ROOT / "config/regra_maxima.json").read_text(encoding="utf-8"))

    def test_motor_mostra_cada_oportunidade_uma_vez(self):
        """28/09: abaixo do motor, a mesma oportunidade aparecia uma vez por dia; e o indicador ficava em 'carregando…'."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertNotIn("dias.filter(x=>x.t).slice(-3)", h)
        self.assertIn('_AM["plat-"+o.id]', h)
        A = json.loads((ROOT / "docs/dados/achados_motores.json").read_text(encoding="utf-8"))["motores"]
        for mid, x in A.items():
            tits = [re.sub(r"[^a-z0-9]", "", e["titulo"].lower())[:60] for e in x.get("ultimas", [])]
            self.assertEqual(len(tits), len(set(tits)), f"{mid} repete oportunidade")
            for e in x.get("ultimas", []):
                self.assertIn("opressor", e, f"{mid}: oportunidade sem destino de opressor")

    def test_radar_so_com_o_fluxo_validado(self):
        """28/09: o Radar lia editais sem validação e chamava programas do catálogo de 'editais possíveis'."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        ini = h.index("RADAR DE RECURSOS DA PÁGINA INICIAL (titular, 28/09)")
        novo = h[ini:h.index("function corTexto(hex){", ini)]
        corpo = novo.split("*/", 1)[1]
        self.assertIn("window._FLUXO", corpo)
        for proibido in ("D.editais", "D.bussola_painel", "D.fontes_ativas", "D._historico"):
            self.assertNotIn(proibido, corpo, proibido)
        self.assertIn("link_oficial", corpo)

    def test_calendario_completo_dia_a_dia_e_emendas(self):
        """28/09: o calendário completo não mostrava as inscrições abertas dia a dia; as emendas tinham sumido."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^function desenhaCal\(", h, re.M)), 1)
        self.assertEqual(len(re.findall(r"^function desenhaGantt\(", h, re.M)), 1)
        self.assertEqual(len(re.findall(r"^function desenhaRadar\(", h, re.M)), 1)
        self.assertIn("CALENDÁRIO COMPLETO, DIA A DIA (titular, 28/09)", h)
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        em = [x for x in F.get("calendario", []) if "Emenda Parlamentar" in x.get("titulo", "")]
        self.assertGreaterEqual(len(em), 3, "emendas parlamentares fora do calendário")
        for x in em:
            self.assertTrue(x.get("inicio") and x.get("fim") and x.get("link_oficial"))


if __name__ == "__main__":
    unittest.main()
