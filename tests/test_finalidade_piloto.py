"""Nova finalidade do Piloto, mapa de cobertura e revezamento das vias (22/09)."""
import json, pathlib, unittest
from src.cobertura import mapa, ja_coberto, instrucao_para_o_piloto, VAZIOS
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteFinalidade(unittest.TestCase):
    def test_o_piloto_nao_concorre_com_os_motores(self):
        c = json.loads((ROOT / "config/cargo_sindico.json").read_text(encoding="utf-8"))
        f = c["finalidade"]
        self.assertIn("NAO concorre com os motores", f["resumo"])
        self.assertIn("1_verificar_e_alimentar", f["duas_missoes"])
        self.assertIn("2_descobrir_o_que_ninguem_busca", f["duas_missoes"])
        self.assertIn("PRIORIDADE", f["duas_missoes"]["1_verificar_e_alimentar"])
        self.assertIn("desperdicio", f["proibido"])
        self.assertGreaterEqual(len(f["rastro_de_edital"]), 5)
        self.assertIn("sites_especializados", f)
        self.assertGreaterEqual(c["parametros"]["resgates_por_voo"], 6)      # verificar vem primeiro

    def test_angulos_procuram_o_que_motor_nao_ve(self):
        m = json.loads((ROOT / "config/motor_sindico.json").read_text(encoding="utf-8"))
        self.assertIn("so vale o que os 29 motores NAO cobrem", m["regra_de_ouro"])
        alvos = {a["alvo"] for a in m["angulos_de_ataque"]}
        self.assertIn("rastro", alvos)                                       # rastro de edital futuro
        self.assertIn("site", alvos)                                         # portal especializado
        texto = " ".join(a["pergunta"].lower() for a in m["angulos_de_ataque"])
        self.assertIn("sem publicar em diario oficial", texto)
        self.assertIn("ainda vai sair", texto)
        self.assertIn("rodape", texto)


class TesteMapaDeCobertura(unittest.TestCase):
    def test_sabe_onde_os_motores_ja_olham(self):
        d = mapa()
        self.assertGreater(d["dominios_cobertos"], 15)
        self.assertIn("não vai a domínio já coberto", d["regra"])
        self.assertGreaterEqual(len(VAZIOS), 6)
        self.assertTrue(all(v.get("vazio") and v.get("porque") for v in VAZIOS))

    def test_reconhece_dominio_coberto(self):
        c, _ = ja_coberto("https://www.in.gov.br/dou/edital")
        self.assertTrue(c)
        self.assertFalse(ja_coberto("https://institutoqualquer.org.br/edital")[0])
        self.assertFalse(ja_coberto("")[0])

    def test_instrucao_entra_no_briefing(self):
        txt = instrucao_para_o_piloto()
        self.assertIn("não perca voo com isto", txt)
        self.assertIn("SEU LUGAR É ONDE ISTO NÃO ALCANÇA", txt)
        src = (ROOT / "src/briefing_piloto.py").read_text(encoding="utf-8")
        self.assertIn("_cobertura()", src)

    def test_achado_coberto_por_motor_vai_para_quarentena(self):
        from src.aprendizados_piloto import MOTIVOS
        self.assertIn("ja_coberto_por_motor", MOTIVOS)
        src = (ROOT / "src/sindico.py").read_text(encoding="utf-8")
        self.assertIn('_quar(_a, "ja_coberto_por_motor"', src)
        self.assertIn("não é trabalho do Piloto", MOTIVOS["ja_coberto_por_motor"])


class TesteRevezamentoDasVias(unittest.TestCase):
    def test_cada_consulta_comeca_numa_via_diferente(self):
        import src.piloto_busca as P
        P.VIAS.unlink(missing_ok=True)
        a = P.vias_da_roda(); b = P.vias_da_roda()
        self.assertTrue(a and b)
        d = json.loads(P.VIAS.read_text(encoding="utf-8"))
        self.assertIn("roda", d)                                              # a roda avança a cada consulta
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("EM REVEZAMENTO", src)
        self.assertIn("nenhuma apanhe o volume inteiro", src)

    def test_via_bloqueada_sai_da_roda_e_volta_depois(self):
        import src.piloto_busca as P
        P.VIAS.unlink(missing_ok=True)
        P._marcar_via("duckduckgo", False)
        d = json.loads(P.VIAS.read_text(encoding="utf-8"))
        s = d["situacao"]["duckduckgo"]
        self.assertEqual(s["bloqueios"], 1); self.assertTrue(s["bloqueada_em"])
        self.assertFalse(P._via_disponivel("duckduckgo", d))                   # descansa
        P._marcar_via("duckduckgo", True, 5)
        d = json.loads(P.VIAS.read_text(encoding="utf-8"))
        self.assertTrue(P._via_disponivel("duckduckgo", d))                    # voltou
        self.assertEqual(d["situacao"]["duckduckgo"]["resultados"], 5)
        self.assertGreaterEqual(P.DESCANSO_MIN, 10)

    def test_so_pula_de_via_quando_a_atual_nao_entrega(self):
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("entregou: a roda para aqui", src)
        self.assertIn("bloqueou: descansa e a roda segue sem ela", src)

    def test_brave_pronto_para_a_chave(self):
        from src.piloto_busca import CHAVES, _por_api
        self.assertEqual(CHAVES["brave"][0], "BRAVE_SEARCH_KEY")
        self.assertIn("api.search.brave.com", CHAVES["brave"][1])
        self.assertEqual(_por_api("brave", "x", 5), [])                        # sem chave não quebra o voo
        w = (ROOT / ".github/workflows/sindico.yml").read_text(encoding="utf-8")
        self.assertIn("BRAVE_SEARCH_KEY: ${{ secrets.BRAVE_SEARCH_KEY }}", w)
