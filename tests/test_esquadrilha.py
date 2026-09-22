"""Esquadrilha do Síndico (22/09): missões sorteadas, abates, avião e posto de comando."""
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
        p = json.loads((ROOT / "config/cargo_sindico.json").read_text(encoding="utf-8"))["parametros"]
        n = len(sortear(None, ["a", "b"]))
        self.assertGreaterEqual(n, p["tarefas_por_ciclo"]["minimo"]); self.assertLessEqual(n, p["tarefas_por_ciclo"]["maximo"])

    def test_abate_so_conta_alvo_novo(self):
        antes = BORDO.read_text(encoding="utf-8") if BORDO.exists() else None
        try:
            abrir_missao({"tipo": "cacar_oportunidade", "motor": "lab-motor", "ordem": 1}, "teste")
            r = fechar_missao("2 alvos", [{"titulo": "Instituto Novo", "onde": "https://x.org/editais", "url": "https://x.org/editais", "novo": True},
                                          {"titulo": "Já conhecido", "onde": "y", "novo": False}], "lição")
            self.assertEqual(r["abates"], 1); self.assertEqual(r["achados"], 2)
            b = bordo(); self.assertEqual(b["abates"]["lab-motor"]["n"], 1)
            self.assertIsNone(b["missao_atual"]); self.assertEqual(b["missoes"][0]["estado"], "pousou")
            pub = json.loads(PUB.read_text(encoding="utf-8"))
            self.assertIn("legenda", pub); self.assertIn("cacar_oportunidade", pub["legenda"])
        finally:
            if antes: BORDO.write_text(antes, encoding="utf-8")

    def test_escopo_atual_sem_verificacao_de_prazo(self):
        c = json.loads((ROOT / "config/cargo_sindico.json").read_text(encoding="utf-8"))
        self.assertTrue(any("prazo" in x for x in c["missao"]["nao_faz_agora"]))
        self.assertTrue(any("motor" in x for x in c["missao"]["faz_agora"]))
        self.assertIn("aleat", c["missao"]["ritmo"].lower())
        src = (ROOT / "src/sindico.py").read_text(encoding="utf-8")
        for f in ("def missao_cacar", "def missao_afiar", "def missao_local", "sortear()", "fechar_missao"):
            self.assertIn(f, src, f)

    def test_aviao_estrelas_e_posto(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("function aviaoDoSindico", "sind-helice", "sind-luneta", "sind-tiro", "@keyframes sind-voo",
                  "function estrelasDeAbate", "mt-abates", "@keyframes est-nasce",
                  "window.abrirPostoSindico", "function desenhaPostoSindico", 'id="sind-posto"',
                  "Esquadrilha do Síndico", "Diário de bordo deste motor", "carregaEsquadrilha"): self.assertIn(x, h, x)
        self.assertIn("aviaoDoSindico(o.id,o.nome)", h)                   # o avião pousa no motor ativo
        self.assertIn("estrelasDeAbate(ab.n", h)                          # estrelas à esquerda, fora da caixa
        self.assertIn("left:-26px", h)


if __name__ == "__main__":
    unittest.main()
