"""Piloto 22/09: Google + DuckDuckGo, prompt único, foco em empresa/ESG e radar de captação."""
import json, pathlib, unittest
from src.piloto_busca import BUSCADORES, _ResGoogle, _similar, inedita, consultas_ja_usadas
from src.radar_piloto import registrar, marcar, publicar, para_o_claude, radar, MARCADORES, RADAR
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteBuscaMultipla(unittest.TestCase):
    def test_so_ficam_os_buscadores_que_respondem(self):
        """Google, Bing, Mojeek e Marginalia saíram: o diagnóstico no servidor provou que
        recusam nosso endereço, e cada um custava até 20 s de espera por voo. O parser do
        Google fica no código, pronto para voltar se a via por API for contratada."""
        from src.piloto_busca import CHAVES
        nomes = [b[0] for b in BUSCADORES]
        self.assertEqual(nomes, ["duckduckgo"])
        self.assertIn("brave", CHAVES); self.assertIn("google_cse", CHAVES)
        p = _ResGoogle(); p.feed('<a href="/url?q=https://institutox.org.br/edital&sa=U">Instituto X — Edital 2026 de apoio</a>')
        self.assertEqual(p.itens[0]["url"], "https://institutox.org.br/edital")
        p2 = _ResGoogle(); p2.feed('<a href="/url?q=https://www.google.com/search?q=x&sa=U">busca</a>')
        self.assertEqual(p2.itens, [])                                    # lixo do próprio buscador não entra
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn('"buscador": nome', src)                            # cada achado diz de onde veio

    def test_prompt_unico_sem_repetir_consulta(self):
        self.assertGreater(_similar("edital instituto apoio projetos sociais", "edital instituto apoio a projetos sociais"), 0.7)
        self.assertLess(_similar("relatório ESG agroindústria Goiás", "edital municipal sazonal cultura"), 0.2)
        usadas = ["edital instituto apoio projetos sociais 2026"]
        self.assertFalse(inedita("edital instituto apoio a projetos sociais 2026", usadas))
        self.assertTrue(inedita("relatório ESG usina de açúcar Goiás projeto social", usadas))
        cfg = json.loads((ROOT / "config/motor_sindico.json").read_text(encoding="utf-8"))
        self.assertLessEqual(cfg["prompt_unico"]["similaridade_maxima"], 0.8)
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("JÁ PERGUNTEI ISTO ANTES", src)                     # o histórico vai no prompt

    def test_foco_em_empresa_esg_e_quatro_niveis(self):
        m = json.loads((ROOT / "config/motor_sindico.json").read_text(encoding="utf-8"))
        niveis = {a["nivel"] for a in m["angulos_de_ataque"]}
        self.assertEqual(niveis, {"regional", "estadual", "nacional", "internacional"})
        perguntas = " ".join(a["pergunta"].lower() for a in m["angulos_de_ataque"])
        for termo in ("esg", "patrocinadora", "edital de seleção de projetos sociais em anos anteriores", "instituto"):
            self.assertIn(termo.split()[0], perguntas)
        self.assertTrue(any("anos anteriores" in a["pergunta"] for a in m["angulos_de_ataque"]))   # edital passado indica recorrência
        self.assertIn("edital de anos anteriores", " ".join(m["foco"]["sempre_procurar"]))
        self.assertGreaterEqual(sum(1 for a in m["angulos_de_ataque"] if a["alvo"] == "empresa"), 7)


class TesteRadarDeCaptacao(unittest.TestCase):
    def test_descoberta_entra_como_a_pesquisar_e_conclui(self):
        antes = RADAR.read_text(encoding="utf-8") if RADAR.exists() else None
        try:
            e = registrar({"titulo": "Instituto Teste", "url": "https://institutoteste.org.br/edital", "porque": "edital aberto"}, "esg_relatorio_go", "sindico-aberto")
            self.assertEqual(e["marcador"], "a_pesquisar"); self.assertGreaterEqual(len(e["a_descobrir"]), 5)
            self.assertIn("relatório ESG", " ".join(e["a_descobrir"]))
            self.assertIn("editais anteriores", " ".join(e["a_descobrir"]))
            self.assertEqual(e["nivel"], "regional")
            fila = [x for x in para_o_claude() if x["chave"] == "institutoteste.org.br"]
            self.assertTrue(fila)
            r = marcar("institutoteste.org.br", "em_pesquisa", "claude")
            self.assertEqual(r["marcador"], "em_pesquisa")
            r = marcar("institutoteste.org.br", "concluido", "claude", {"esg": {"tem_relatorio": True}, "potencial": "alto", "cobre_tudo": True})
            self.assertEqual(r["marcador"], "concluido"); self.assertTrue(r["pesquisado_em"]); self.assertEqual(r["potencial"], "alto")
            self.assertFalse([x for x in para_o_claude() if x["chave"] == "institutoteste.org.br"])   # sai da fila
            self.assertEqual(set(MARCADORES), {"a_pesquisar", "em_pesquisa", "concluido"})
            p = publicar(); self.assertIn("por_marcador", p)
        finally:
            if antes: RADAR.write_text(antes, encoding="utf-8")

    def test_radar_e_lista_propria_sem_furar_o_ranking(self):
        """O ranking oficial tem 100 posições ordenadas por pontuação: o Piloto não fura a fila.
        As descobertas viram lista própria e só entram no ranking depois da pesquisa concluída."""
        rk = json.loads((ROOT / "biblioteca_alexandria/empresas/ranking_destinacao_tributaria.json").read_text(encoding="utf-8"))
        self.assertEqual(rk["total"], 100); self.assertEqual(len(rk["empresas"]), 100)
        self.assertFalse(any(str(x.get("origem", "")).startswith("piloto") for x in rk["empresas"]))
        rd = json.loads((ROOT / "biblioteca_alexandria/empresas/radar_captacao.json").read_text(encoding="utf-8"))
        self.assertIn("entram no ranking oficial quando a pesquisa concluir", rd["regra"])
        self.assertTrue(all(e.get("marcador") in MARCADORES for e in rd["empresas"]))
        pc = (ROOT / "src/pacote_conselho.py").read_text(encoding="utf-8")
        self.assertIn("Radar de captação", pc); self.assertIn("para_o_claude", pc)
        sd = (ROOT / "src/sindico.py").read_text(encoding="utf-8")
        self.assertIn("from .radar_piloto import registrar", sd)

    def test_posto_so_na_inicial_e_na_bussola(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertEqual(h.count('id="pil-posto"'), 1); self.assertEqual(h.count('id="pil-posto-bussola"'), 1)
        self.assertIn('desenhaPostoPiloto("pil-posto")', h); self.assertIn('desenhaPostoPiloto("pil-posto-bussola")', h)
        self.assertIn("Radar de captação", h); self.assertIn("a pesquisar", h)
        self.assertIn("carregaRadar", h)
