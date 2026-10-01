"""30/09: a curadoria dos livros trocou ids de opressores pesquisados (12 parâmetros) e a regeneração desligou
os 'órfãos' — 329 ligados viraram 105. Pesquisado nunca some; todo ligado tem livro; todo JSON é válido."""
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePesquisadosProtegidos(unittest.TestCase):
    def test_pesquisados_continuam_ligados_com_parametros(self):
        from src.parametros_opressores import carregar
        uteis = {i for i, r in carregar().items() if r.get("decisao") != "D"}
        L = json.loads((ROOT / "estado/opressores.json").read_text(encoding="utf-8"))["ligados"]
        com = {k for k, v in L.items() if v.get("parametros")}
        self.assertGreaterEqual(len(com), 200, "opressores pesquisados perderam os parâmetros")

    def test_todo_ligado_tem_livro(self):
        L = json.loads((ROOT / "estado/opressores.json").read_text(encoding="utf-8"))["ligados"]
        C = {x["id"] for x in json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]}
        self.assertEqual([k for k in L if k not in C], [])

    def test_curadoria_protege_pesquisado(self):
        for f, trecho in (("src/livros_opressores.py", 'and not x.get("parametros")'), ("src/opressores_repositorio.py", 'x.get("parametros") or not'),
                          ("src/motores.py", 'x.get("parametros") or not')):
            self.assertIn(trecho, (ROOT / f).read_text(encoding="utf-8"), f)

    def test_dados_json_validos(self):
        for f in ("biblioteca_alexandria/fontes/motores.json", "estado/opressores.json", "docs/dados/motores.json", "docs/dados/fluxo_oportunidades.json"):
            json.loads((ROOT / f).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
