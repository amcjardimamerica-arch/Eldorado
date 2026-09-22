"""Missão de expansão: descobrir LUGARES, não editais (22/09)."""
import json, pathlib, unittest
from src.prospeccao import (catalogar_patrocinadores, validar_empresa, registrar, promover_a_motor,
                            publicar, fontes, TIPOS, NIVEIS, TRILHAS, FONTES)
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteCatalogoDePatrocinadores(unittest.TestCase):
    def test_tira_apoiadores_do_site_de_outra_entidade(self):
        html = ('<footer><h3>Nossos apoiadores e patrocinadores</h3>'
                '<a href="https://agroluz.com.br"><img alt="Agroluz Alimentos"></a>'
                '<a href="https://bancox.com.br">Banco X</a>'
                '<a href="https://facebook.com/ong">Face</a>'
                '<a href="https://www.gov.br/cultura">Ministério</a></footer>')
        ps = catalogar_patrocinadores(html, "https://ong.org.br/apoiadores")
        doms = [p["dominio"] for p in ps]
        self.assertIn("agroluz.com.br", doms); self.assertIn("bancox.com.br", doms)
        self.assertNotIn("facebook.com", doms)                     # rede social não é patrocinador
        self.assertTrue(all("gov.br" not in d for d in doms))      # órgão público já tem motor
        self.assertEqual(ps[0]["nome"], "Agroluz Alimentos")       # pega o nome do alt da imagem

    def test_link_sem_contexto_de_apoio_nao_entra(self):
        html = '<a href="https://qualquer.com.br">leia mais</a>'
        self.assertEqual(catalogar_patrocinadores(html, "https://ong.org.br"), [])


class TesteValidacaoNoSiteDaEmpresa(unittest.TestCase):
    def test_le_o_site_da_propria_empresa_sem_buscador(self):
        def ler(url, tempo=15):
            if "sustentabilidade" in url:
                return "Relatório de sustentabilidade ESG com nosso investimento social. " * 8
            if url.endswith("/editais"):
                return "Edital de seleção de projetos para organizações da sociedade civil. " * 6
            return ""
        v = validar_empresa("agroluz.com.br", ler=ler)
        self.assertIn("esg", v["tipos"]); self.assertIn("edital_proprio", v["tipos"])
        self.assertTrue(v["tem_programa"]); self.assertTrue(v["vira_motor"])
        self.assertTrue(v["tipos"]["esg"]["trecho"])               # só afirma o que está escrito
        self.assertTrue(v["tipos"]["esg"]["pagina"].startswith("https://agroluz.com.br"))
        self.assertGreaterEqual(len(TRILHAS), 12)

    def test_empresa_sem_programa_diz_por_que(self):
        v = validar_empresa("vazia.com.br", ler=lambda u, tempo=15: "")
        self.assertFalse(v["tem_programa"])
        self.assertIn("nenhuma das trilhas", v["porque_nao"])

    def test_os_seis_tipos_de_recurso_tem_porta_de_entrada(self):
        self.assertEqual(set(TIPOS), {"incentivo_fiscal", "patrocinio", "edital_proprio",
                                      "instituto_fundacao", "esg", "doacao"})
        for t, d in TIPOS.items():
            self.assertTrue(d["rotulo"] and d["porta"] and d["pistas"], t)
        self.assertIn("setor fiscal", TIPOS["incentivo_fiscal"]["porta"])   # porta diferente por tipo
        self.assertIn("marketing", TIPOS["patrocinio"]["porta"])


class TesteQuatroNiveis(unittest.TestCase):
    def test_local_estadual_federal_internacional(self):
        self.assertEqual(set(NIVEIS), {"local", "estadual", "federal", "internacional"})
        for n, d in NIVEIS.items():
            self.assertTrue(d["rotulo"] and d["onde_procurar"] and d["vantagem"], n)
        self.assertIn("Goiânia", NIVEIS["local"]["rotulo"])
        self.assertIn("pouca concorrência", NIVEIS["internacional"]["vantagem"])


class TesteFonteViraMotor(unittest.TestCase):
    def test_o_caminho_todo_do_rastro_ao_motor(self):
        antes_f = FONTES.read_text(encoding="utf-8") if FONTES.exists() else None
        cfgp = ROOT / "config/rotas_motores.json"
        antes_c = cfgp.read_text(encoding="utf-8")
        try:
            v = {"tipos": {"edital_proprio": {"pagina": "https://t.com.br/editais", "pista": "edital", "trecho": "x"}},
                 "tem_programa": True, "vira_motor": True}
            it = registrar({"nome": "Teste SA", "dominio": "t.com.br", "site": "https://t.com.br",
                            "onde_vi": "https://ong.org/apoio"}, v, nivel="estadual", angulo="apoiador_no_rodape")
            self.assertEqual(it["estado"], "validada")
            self.assertTrue(it["portas"]); self.assertGreater(it["pontos"], 0)
            self.assertIn("https://ong.org/apoio", it["rastros"])   # guarda de onde veio o rastro
            m = promover_a_motor("t.com.br")
            self.assertTrue(m.get("motor_criado"))
            cfg = json.loads(cfgp.read_text(encoding="utf-8"))
            novo = (cfg.get("motores") or cfg)[m["motor_criado"]]
            self.assertEqual(novo["origem"], "prospecção do Piloto")
            self.assertIn("colheita diária, não voo", novo["nota"])
            self.assertEqual(fontes()["itens"]["t.com.br"]["estado"], "promovida_a_motor")
        finally:
            cfgp.write_text(antes_c, encoding="utf-8")
            if antes_f: FONTES.write_text(antes_f, encoding="utf-8")
            elif FONTES.exists(): FONTES.unlink()

    def test_so_promove_com_edital_proprio_comprovado(self):
        r = promover_a_motor("nao-existe.com.br")
        self.assertIn("erro", r)

    def test_meta_diaria_de_aumentar_os_lugares(self):
        p = publicar()
        self.assertIn("mais lugares para olhar do que começou", p["meta"])
        for c in ("descobertas_hoje", "promovidas_a_motor", "por_nivel", "por_tipo"):
            self.assertIn(c, p, c)

    def test_missao_de_expansao_esta_no_voo(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("def missao_prospeccao", src)
        self.assertIn("descobrir LUGARES novos, não editais", src)
        self.assertIn("PÁGINAS QUE LISTAM APOIADORES", src)
        self.assertIn("promover_a_motor", src)


class TesteRenomeacao(unittest.TestCase):
    def test_sindico_virou_piloto_no_sistema(self):
        self.assertTrue((ROOT / "src/piloto.py").exists())
        self.assertTrue((ROOT / "estado/piloto").is_dir())
        self.assertFalse((ROOT / "estado/sindico").exists())
        self.assertFalse((ROOT / "src/sindico.py").exists())
        self.assertTrue((ROOT / "config/cargo_piloto.json").exists())
        self.assertTrue((ROOT / "config/motor_piloto.json").exists())
        self.assertTrue((ROOT / ".github/workflows/piloto.yml").exists())

    def test_nenhuma_referencia_solta_no_codigo(self):
        import re
        for p in list((ROOT / "src").rglob("*.py")) + list((ROOT / ".github/workflows").rglob("*.yml")):
            t = p.read_text(encoding="utf-8")
            sobra = [l for l in t.split("\n") if re.search(r"\bsindico\b", l) and "sindico-aberto" not in l]
            self.assertEqual(sobra, [], f"{p.name}: {sobra[:1]}")
