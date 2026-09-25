"""Esquadrilha do Piloto (22/09): missões sorteadas, abates, avião e posto de comando."""
import json, pathlib, unittest
from src.esquadrilha import sortear, abrir_missao, fechar_missao, bordo, resumo, MISSOES, BORDO, PUB
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteMissoes(unittest.TestCase):
    def test_sorteio_aleatorio_com_rodizio(self):
        m = sortear(8, ["a", "b", "c", "d"])
        self.assertEqual(len(m), 8)
        self.assertTrue(all(x["tipo"] in MISSOES for x in m))
        self.assertGreaterEqual(len({x["tipo"] for x in m}), 2)          # não é sempre a mesma tarefa
        self.assertGreaterEqual(len({x["motor"] for x in m}), 3)          # rodízio entre motores
        p = json.loads((ROOT / "config/cargo_piloto.json").read_text(encoding="utf-8"))["parametros"]
        n = len(sortear(None, ["a", "b"]))
        self.assertGreaterEqual(n, p["tarefas_por_ciclo"]["minimo"]); self.assertLessEqual(n, p["tarefas_por_ciclo"]["maximo"])

    def test_abate_so_conta_alvo_novo(self):
        antes = BORDO.read_text(encoding="utf-8") if BORDO.exists() else None
        BORDO.unlink(missing_ok=True)                                   # teste isolado: bordo limpo
        try:
            abrir_missao({"tipo": "cacar_oportunidade", "motor": "ensaio-motor", "ordem": 1}, "teste")
            # 24/09: abate precisa de tipo — edital com prazo aberto (ouro) ou empresa (prata)
            r = fechar_missao("2 alvos", [{"titulo": "Instituto Novo", "onde": "https://x.org/editais", "url": "https://x.org/editais", "novo": True, "fim": "2099-12-31"},
                                          {"titulo": "Já conhecido", "onde": "y", "novo": False}], "lição")
            self.assertEqual(r["abates"], 1); self.assertEqual(r["achados"], 2)
            b = bordo(); self.assertEqual(b["abates"]["ensaio-motor"]["n"], 1)
            self.assertIsNone(b["missao_atual"]); self.assertEqual(b["missoes"][0]["estado"], "pousou")
            pub = json.loads(PUB.read_text(encoding="utf-8"))
            self.assertIn("legenda", pub); self.assertIn("cacar_oportunidade", pub["legenda"])
        finally:
            if antes: BORDO.write_text(antes, encoding="utf-8")

    def test_escopo_atual_sem_verificacao_de_prazo(self):
        c = json.loads((ROOT / "config/cargo_piloto.json").read_text(encoding="utf-8"))
        self.assertTrue(any("prazo" in x for x in c["missao"]["nao_faz_agora"]))
        self.assertTrue(any("motor" in x for x in c["missao"]["faz_agora"]))
        self.assertIn("aleat", c["missao"]["ritmo"].lower())
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        for f in ("def missao_cacar", "def missao_afiar", "def missao_local", "\"tipo\": \"catalogar\"", "fechar_missao"):
            self.assertIn(f, src, f)

    def test_aviao_estrelas_e_posto(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("function aviaoDoPiloto", "pil-helice", "pil-luneta", "pil-tiro", "@keyframes pil-voo",
                  "function estrelasDeAbate", "mt-abates", "@keyframes est-nasce",
                  "window.abrirPostoPiloto", "function desenhaPostoPiloto", 'id="pil-posto"',
                  "Esquadrilha do Piloto", "Diário de bordo deste motor", "carregaEsquadrilha"): self.assertIn(x, h, x)
        self.assertIn("function aviaoDoPiloto", h)                          # o avião existe...
        self.assertNotIn("voa?aviaoDoPiloto", h)                            # ...mas não dentro de cada motor da lista                   # o avião pousa no motor ativo
        self.assertIn("estrelasDeAbate(ab.n", h)                          # estrelas à esquerda, fora da caixa
        self.assertIn("right:calc(100% + 10px)", h)


if __name__ == "__main__":
    unittest.main()


class TesteMotor29EFoco(unittest.TestCase):
    def test_sindico_voa_so_nos_quatro_motores(self):
        c = json.loads((ROOT / "config/cargo_piloto.json").read_text(encoding="utf-8"))
        ids = c["parametros"]["motores_do_piloto"]["ids"]
        self.assertEqual(set(ids), {"empresas-incentivadas", "motor-gife", "motor-patrocinio", "piloto-aberto"})
        self.assertIn("releem o que já está mapeado", c["parametros"]["motores_do_piloto"]["porque"])
        m = sortear(10)
        self.assertTrue({x["motor"] for x in m} <= set(ids), "o Piloto saiu do escopo")
        src = (ROOT / "src/esquadrilha.py").read_text(encoding="utf-8")
        self.assertIn("motores_do_piloto", src)

    def test_motor29_tem_lexico_angulos_e_exige_site_oficial(self):
        m = json.loads((ROOT / "config/motor_piloto.json").read_text(encoding="utf-8"))
        self.assertEqual(m["rank"], 29)
        self.assertGreaterEqual(len(m["lexico_camada1_positivos"]), 30)
        self.assertGreaterEqual(len(m["lexico_camada1_veto"]), 10)
        self.assertGreaterEqual(len(m["angulos_de_ataque"]), 10)
        self.assertTrue(all(a.get("pergunta") and a.get("alvo") for a in m["angulos_de_ataque"]))
        # Os ângulos mudaram com a finalidade: o Piloto deixou de caçar o que os motores já
        # cobrem (sazonal público, Lucro Real) e passou a procurar o que ninguém busca —
        # rastro de edital futuro, patrocinador no rodapé, instituto sem divulgação.
        self.assertTrue(any(a["alvo"] == "rastro" for a in m["angulos_de_ataque"]))
        self.assertTrue(any(a["alvo"] == "site" for a in m["angulos_de_ataque"]))
        self.assertTrue(any("internacional" in a["id"] for a in m["angulos_de_ataque"]))
        self.assertIn("NAO cobrem", m["regra_de_ouro"])
        self.assertIn("SITE OFICIAL", m["regra_de_abate"])
        self.assertTrue(m["aprendizado"]["pode_criar_termos"])            # pode propor termos novos
        self.assertIn("3 execuções", m["memoria_negativa"]["regra"])
        from src.sensores import registro, lexico_camada1
        s = [x for x in registro() if x["id"] == "plat-piloto-aberto"]
        self.assertTrue(s, "o motor 29 precisa existir como sensor")
        t, v = lexico_camada1(s[0]); self.assertGreaterEqual(len(t), 40)
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("def missao_motor29", src); self.assertIn("def _angulo_do_dia", src)
        pb = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("_oficial(b[\"url\"])", pb)                              # abate só com site oficial
        self.assertIn("def buscar(", pb); self.assertIn("def ler_pagina(", pb)  # busca REAL na internet
        self.assertIn("QUESTIONAMENTO NOVO", pb)

    def test_helice_clicavel(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("window.darPartida", "-helice-bt", "pil-pa", "@keyframes pil-pa-gira", "pil-fumaca",
                  "contato!", "Motores ligados", "motores 26, 27, 28 e 29"): self.assertIn(x, h, x)
