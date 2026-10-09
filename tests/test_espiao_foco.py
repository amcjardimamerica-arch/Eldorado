"""09/10 (titular): Piloto - Espião só caça editais de empresas, oportunidades de empresas e internacionais fora
dos motores; buscas criativas por famílias; rede neural a cada 100 voos; empresas novas vão ao campo de empresas."""
import json, random, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import espiao_foco as E

PAGINAS = {
    "https://www.institutoexemplo.org.br/edital-2026": ("Edital 2026 de projetos sociais | Instituto Exemplo",
        "O Instituto Exemplo abre o edital 2026 para organizações da sociedade civil. Inscrições até 30/11/2026. Regulamento completo."),
    "https://www.supermercadosx.com.br/responsabilidade": ("Responsabilidade social – Rede Supermercados X",
        "A rede apoia entidades com doação de alimentos para instituições sociais e ONGs de Goiânia. Programa de apoio contínuo."),
    "https://www.foundation-abc.org/grants": ("Grants for Brazil | ABC Foundation",
        "Call for proposals: grants for NGOs in Brazil. Nonprofit organizations may apply until December 2026."),
    "https://www.goiania.go.gov.br/edital": ("Edital da prefeitura", "Edital para OSC de assistência social. Inscrições abertas."),
    "https://prosas.com.br/editais/123": ("Edital no Prosas", "Edital para ONGs, inscrições abertas."),
    "https://www.jornal.com.br/noticia": ("Notícia qualquer", "Texto sem nada a ver."),
}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(E, k) for k in ("CEREBRO", "CANDIDATAS", "EMPRESAS_ESPIAO", "AVALIACAO", "nota_rede", "fora_dos_motores")}
        E.CEREBRO = T / "c.json"; E.CANDIDATAS = T / "cand.json"; E.EMPRESAS_ESPIAO = T / "emp.json"; E.AVALIACAO = T / "av.json"
        E.nota_rede = lambda t, x, u: 0.8
        orig_fora = self.orig["fora_dos_motores"]
        E.fora_dos_motores = lambda u: (False, "já vigiado pelo motor m1") if "prosas" in u else orig_fora(u)

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(E, k, v)
        self.tmp.cleanup()

    def _missao(self, conhecidas=()):
        return E.missao(1, buscar=lambda q, maximo=8: [{"url": u, "titulo": t} for u, (t, _x) in PAGINAS.items()],
                        ler_pagina=lambda u, limite=9000: PAGINAS[u][1], conhecida=lambda n: n in conhecidas, rnd=random.Random(3))


class TesteFiltroEFrentes(Base):
    def test_so_privado_e_internacional_fora_dos_motores(self):
        q, ach, licao = self._missao()
        urls = {a["url"] for a in ach}
        self.assertNotIn("https://www.goiania.go.gov.br/edital", urls, "governo é dos motores")
        self.assertNotIn("https://prosas.com.br/editais/123", urls, "agregador / já vigiado por motor")
        self.assertNotIn("https://www.jornal.com.br/noticia", urls, "sem sinal de oportunidade para OSC")
        fr = {a["url"]: a["frente"] for a in ach}
        self.assertEqual(fr["https://www.institutoexemplo.org.br/edital-2026"], "editais_de_empresas")
        self.assertEqual(fr["https://www.supermercadosx.com.br/responsabilidade"], "oportunidades_de_empresas")
        self.assertEqual(fr["https://www.foundation-abc.org/grants"], "internacional")

    def test_empresas_novas_no_campo_de_empresas_e_candidatas(self):
        self._missao(conhecidas={"Instituto Exemplo"})
        emp = json.loads(E.EMPRESAS_ESPIAO.read_text())["achados"]
        nomes = {e["empresa"] for e in emp}
        self.assertIn("Rede Supermercados X", nomes); self.assertIn("ABC Foundation", nomes)
        self.assertNotIn("Instituto Exemplo", nomes, "empresa já conhecida (cadastro / incentivo) não é catalogada de novo")
        self.assertTrue(all(e["fora_da_lista_de_incentivo"] for e in emp))
        mod = {e["empresa"]: e["modalidade"] for e in emp}
        self.assertEqual(mod["Rede Supermercados X"], "doação"); self.assertEqual(mod["ABC Foundation"], "internacional")
        cand = json.loads(E.CANDIDATAS.read_text())["candidatas"]
        self.assertEqual({c["frente"] for c in cand}, {"editais_de_empresas", "internacional"}, "edital e internacional vão ao Interceptador")
        self._missao(conhecidas={"Instituto Exemplo"})
        self.assertEqual(len(json.loads(E.EMPRESAS_ESPIAO.read_text())["achados"]), len(emp), "não repete a mesma empresa")

    def test_patrocinio_agrega_as_empresas_do_espiao(self):
        s = (ROOT / "src/patrocinios.py").read_text(encoding="utf-8")
        self.assertIn('espiao_empresas.json', s)
        self.assertIn("dados/empresas/go/espiao_empresas.json", (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8"))


class TesteCerebro(Base):
    def test_buscas_criativas_de_varias_familias(self):
        c = E.cerebro(); rnd = random.Random(1)
        qs = [E.escolher(c, rnd) for _ in range(60)]
        self.assertGreaterEqual(len({f for f, _ in qs}), 6, "várias famílias de busca")
        self.assertGreaterEqual(len({q for _, q in qs}), 50, "consultas quase sempre diferentes")
        self.assertTrue(any(f.startswith("internacional") for f, _ in qs))

    def test_aprende_e_avalia_a_cada_100_voos(self):
        self._missao()
        c = E.cerebro()
        usadas = [f for f, v in c["familias"].items() if v["usos"]]
        self.assertEqual(len(usadas), 1); self.assertGreater(c["familias"][usadas[0]]["a"], 1.0, "família que rendeu ganha peso")
        for _ in range(99):
            r = E.inicio_do_voo()
        self.assertNotIn("avaliacao", r)
        r = E.inicio_do_voo()
        self.assertIn("avaliacao", r, "no 100º voo: avaliação")
        av = r["avaliacao"]
        self.assertTrue(av["familias"]); self.assertGreaterEqual(av["mutacoes_criadas"], 1, "mutações das melhores consultas")
        self.assertEqual(E.cerebro()["voos_desde_avaliacao"], 0)
        self.assertTrue(json.loads(E.AVALIACAO.read_text())["avaliacoes"])

    def test_consulta_que_falhou_tres_vezes_e_aposentada(self):
        c = E.cerebro(); c["consultas"] = {"x": {"usos": 3, "achados": 0}}; c["mutacoes"] = ["x"]
        self.assertNotEqual(E.escolher(c, random.Random(0))[1], "x")


class TesteVoo(unittest.TestCase):
    def test_voo_usa_so_a_missao_nova_com_foco_ativo(self):
        s = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn('plano.append({"tipo": "espionar"', s)
        self.assertIn('if m["tipo"] == "espionar":', s)
        self.assertIn('vagas = 0 if _foco.get("ativo")', s)
        self.assertTrue(json.loads((ROOT / "config/espiao_foco.json").read_text(encoding="utf-8"))["ativo"])


if __name__ == "__main__":
    unittest.main()
