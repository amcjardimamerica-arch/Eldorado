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
        cal = h[h.index("CALENDÁRIO COMPLETO, DIA A DIA (titular, 28/09)"):h.index("function corTexto(hex){")]
        self.assertNotIn("ver todas", cal, "o calendário não pode esconder oportunidade")
        self.assertIn("cv-vaga", cal, "cada oportunidade precisa de linha fixa (vaga vazia nos dias em que não está aberta)")
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        em = [x for x in F.get("calendario", []) if "Emenda Parlamentar" in x.get("titulo", "")]
        self.assertGreaterEqual(len(em), 3, "emendas parlamentares fora do calendário")
        for x in em:
            self.assertTrue(x.get("inicio") and x.get("fim") and x.get("link_oficial"))

    def test_gravacao_dos_voos_nao_regrava_codigo(self):
        """28/09: a gravação de um voo do Espião desfez uma correção de código (reset --soft + git add -A geral)."""
        for w in (ROOT / ".github/workflows").glob("*.yml"):
            y = w.read_text(encoding="utf-8")
            self.assertNotIn("reset --soft", y, f"{w.name}: reset --soft leva a árvore velha no commit")
            self.assertNotIn("|| git add -A\n", y, f"{w.name}: 'git add -A' geral como plano B")
            self.assertNotRegex(y, r"git add -A;\s*git commit", f"{w.name}: 'git add -A' geral na recomposição")

    def test_quadros_dos_motores_contidos(self):
        """28/09: a coluna do meio do quadro do motor esticava com a linha mais longa e o calendário vazava."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn(".mt-item{grid-template-columns:44px minmax(0,1fr) 40px}", h)
        self.assertIn("#mt-lista .mt-ach{display:grid", h)
        self.assertIn('class="mt-ach mt-ach1"', h, "oportunidade encontrada em uma linha: nome, prazo, opressor, site oficial")

    def test_oportunidades_abertas_do_fluxo_e_opressores(self):
        """28/09: os cartões de oportunidades abertas liam o conjunto antigo; toda oportunidade com seleção precisa de
        motor opressor (ou do motivo da dispensa); o quadro 'Aguardando verificação da IA' saiu."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("function _desenhaAbertasFluxo(", h)
        self.assertIn("_desenhaAbertasFluxo();       //", h)
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        its = [x for v in F["itens_por_uf"].values() for x in v]
        sem = [x["titulo"][:60] for x in its if not x.get("opressor") and not x.get("opressor_dispensa")]
        self.assertEqual(sem, [], "oportunidade aberta sem motor opressor e sem motivo de dispensa")
        from src.opressores_repositorio import dispensa, chave
        self.assertIsNone(dispensa({"titulo": "Patrocínios", "tipo": "empresa/instituto"}))   # 01/10 (titular): toda oportunidade mapeada vira livro
        self.assertIsNone(dispensa({"titulo": "Edital de seleção de projetos 2026", "tipo": "empresa/instituto"}))
        self.assertEqual(chave("Edital nº 02/2026 — Prêmio X"), chave("Edital nº 05/2025 — Prêmio X"))

    def test_checklist_12_itens_e_temas(self):
        """28/09: os cartões perderam o checklist dos 12 itens e a separação por temas com as cores das áreas."""
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        its = [x for v in F["itens_por_uf"].values() for x in v]
        for x in its:
            self.assertEqual(len(x.get("checklist") or {}), 12, x["titulo"][:50])
        self.assertGreater(sum(1 for x in its if x.get("area")), len(its) * 0.7, "tema identificado em menos de 70%")
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('class="oa-sec"', h); self.assertIn("oa-ki", h)

    def test_bussola_numeros_reais(self):
        """28/09: os cartões da Bússola liam o conjunto antigo; 'fontes monitoradas' não batia com os opressores ligados."""
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        O = F.get("opressores") or {}
        self.assertEqual(O.get("abertas_sem_opressor_nem_dispensa"), 0)
        C = {x["id"] for x in json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]}
        L = json.loads((ROOT / "estado/opressores.json").read_text(encoding="utf-8"))["ligados"]
        self.assertEqual([k for k in L if k not in C], [], "opressor ligado que não existe no catálogo")
        self.assertEqual(O.get("ligados"), len(L))
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        cards = h[h.index("function desenhaBzCards(){"):h.index('$("bz-cards").innerHTML=cards.map(')]
        self.assertIn("FX.opressores", cards); self.assertNotIn("eds.filter(e=>situacaoDe(e)", cards)
        self.assertIn("fr(OP.ligados??0,OP.catalogo??0)", cards, "fontes monitoradas: ligados / disponíveis na Biblioteca")
        self.assertNotIn('<div class="s ${c[4]}">', h, "cartão da Bússola sem texto além do título")

    def test_pagina_nao_recarrega_sozinha(self):
        """28/09: a autoatualização do código recarregava a página e reiniciava a tela. Só por clique do titular."""
        import re as _re
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        automaticos = [l for l in h.split("\n") if _re.search(r"location\.(reload|replace)\(|location\.href\s*=", l) and "onclick" not in l]
        self.assertEqual(automaticos, [], "recarregamento automático da página")
        self.assertIn("window.scrollTo(0,_y);", h, "atualização dos dados preserva a posição da tela")

    def test_funcoes_chamadas_pela_tela_existem(self):
        """28/09: o filtro de estado das oportunidades abertas chamava uma função fora do escopo global; o botão
        'Ver fonte por fonte' chamava uma função que nunca existiu."""
        import re as _re
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for f in ("desenhaAbertasFluxo", "abrePrazos"):
            self.assertIn(f"window.{f}=", h, f"{f} precisa estar no escopo global (é chamada pela tela)")

    def test_motores_nao_param_por_agenda_perdida(self):
        """28/09: o gerador dos motores quebrava com os repositórios de oportunidade (KeyError) e o calendário de TODOS
        parou em 27/09; o agendador perdia o dia quando o GitHub pulava o horário exato."""
        import importlib.util
        src = (ROOT / "src/motores.py").read_text(encoding="utf-8")
        self.assertIn("def _neutro(x: dict) -> dict:", src)
        self.assertIn("{k: m.get(k) for k in (", src)
        sp = importlib.util.spec_from_file_location("ag", ROOT / "scripts/agenda_motores.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        self.assertTrue(hasattr(m, "recuperar"))
        y = (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8")
        self.assertIn('"0 6 * * 0"', y); self.assertIn("motor-gife|motor-patrocinio", y)

    def test_opressores_mesma_contagem_em_todo_lugar(self):
        """28/09: cartão 317/994, painel dos opressores 774 acesos e painel de busca 366 — três contagens diferentes."""
        M = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8"))
        L = json.loads((ROOT / "estado/opressores.json").read_text(encoding="utf-8"))["ligados"]
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]
        self.assertEqual(M["resumo"]["total"], len(C)); self.assertEqual(M["resumo"]["ligados"], len(L))
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('return m?m.proximidade==="ligado":true;', h, "opressor aceso = ligado; motor regular sempre aceso")
        self.assertIn('id="mo-uf"', h, "filtro por estado dos motores opressores")

    def test_separacao_internacional(self):
        """28/09: separação e filtro das oportunidades internacionais nos motores opressores."""
        from src.opressores_repositorio import internacional
        self.assertTrue(internacional({"programa": "Ford Foundation"}))
        self.assertTrue(internacional({"programa": "União Europeia – Erasmus+"}))
        self.assertFalse(internacional({"programa": "Editais FICA Goiás — Festival Internacional de Cinema Ambiental"}))
        self.assertFalse(internacional({"programa": "Edital Secult Goiás", "pagina": "https://goias.gov.br/cultura"}))
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('oi.value="INT"', h); self.assertIn('muf==="INT"?!!m.internacional', h)


if __name__ == "__main__":
    unittest.main()
