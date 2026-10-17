"""11/10/2026 (titular): uma oportunidade = um livro; duplicatas têm um único livro, o da canônica."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import unificar_livros as U
from src import livros_repositorio as O


def L(i, prog, hist, **kw):
    return {"id": i, "programa": prog, "orgao": kw.pop("orgao", ""), "pagina": kw.pop("pagina", "https://orgao.go.gov.br/x"),
            "historico": [{"id": h, "titulo": prog} for h in hist], "criado_em": kw.pop("criado_em", "2026-10-01"), **kw}


class TesteUnificar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.o = (U.CAT, U.LIG, U.REL, O.canonica_por_revisao)
        U.CAT = T / "c.json"; U.LIG = T / "l.json"; U.REL = T / "r.json"
        U.LIG.write_text(json.dumps({"ligados": {"op-b": {"desde": "2026-10-01"}}}))
        O.canonica_por_revisao = lambda: {"dup1": "can1", "dup2": "can2"}

    def tearDown(self):
        U.CAT, U.LIG, U.REL, O.canonica_por_revisao = self.o; self.tmp.cleanup()

    def test_regras(self):
        cat = [L("op-a", "Aviso de Chamamento Público nº 4/2026 de Goiatuba", ["can1"]),
               L("op-b", "Edital nº 004/2026 de Goiatuba", ["dup1"]),                         # grupo 1: dois livros → funde
               L("op-c", "Seleção de projetos culturais PNAB Anápolis", ["dup2"]),             # grupo 2: só na duplicata → religa
               L("op-d", "Aviso de Chamamento Público", ["x9"]), L("op-e", "Aviso de Chamamento Público Nº 1/2026", ["x9"], atual="x9"),
               L("op-f", "Prêmio LED Globo 2027", ["y1"]), L("op-g", "Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão", ["y1"]),
               L("op-h", "Programa X de apoio a projetos sociais", [], ids_juntados=["a", "a", "b", "a"])]
        U.CAT.write_text(json.dumps({"motores": cat}))
        r = U.unificar()
        M = {m["id"]: m for m in json.loads(U.CAT.read_text())["motores"]}
        self.assertNotIn("op-b", M, "livro da duplicata absorvido"); self.assertIn("op-a", M)
        self.assertIn("op-b", M["op-a"]["ids_juntados"]); self.assertIn("op-a", json.loads(U.LIG.read_text())["ligados"], "vínculo de leitura passa ao livro que fica")
        self.assertIn("can2", [h["id"] for h in M["op-c"]["historico"]], "religado à canônica")
        self.assertEqual(sum(1 for m in M.values() for h in m.get("historico") or [] if h["id"] == "x9"), 1, "genérico: fica num só, sem fundir")
        self.assertIn("op-d", M); self.assertIn("op-e", M)
        self.assertEqual(sum(1 for i in ("op-f", "op-g") if i in M), 1, "mesmo programa em dois livros: funde")
        self.assertEqual(M["op-h"]["ids_juntados"], ["a", "b"])
        self.assertEqual(r["resumo"]["oportunidades_com_mais_de_um_livro_depois"], 0)


class TesteCriador(unittest.TestCase):
    def test_canonica_e_fusao_sem_repeticao(self):
        src = (ROOT / "src/livros_repositorio.py").read_text(encoding="utf-8")
        self.assertIn("duplicata → o livro da canônica", src); self.assertIn("agrupar_duplicatas", src)
        from src.curadoria_biblioteca import _juntar
        s = {"id": "s", "ids_juntados": ["o"]}; _juntar(s, {"id": "o", "ids_juntados": ["o"]})
        self.assertEqual(s["ids_juntados"], ["o"])
        self.assertIn("from .unificar_livros import unificar", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
