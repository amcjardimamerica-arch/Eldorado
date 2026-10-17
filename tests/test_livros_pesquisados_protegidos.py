"""30/09: a curadoria dos livros trocou ids de livros pesquisados (12 parâmetros) e a regeneração desligou
os 'órfãos' — 329 ligados viraram 105. Pesquisado nunca some; todo ligado tem livro; todo JSON é válido."""
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePesquisadosProtegidos(unittest.TestCase):
    def test_pesquisados_continuam_ligados_com_parametros(self):
        """01/10: todo livro pesquisado que continua na Biblioteca (dentro da abrangência) mantém os 12 parâmetros."""
        from src.livros_parametros import carregar
        C = {x["id"]: x for x in json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]}
        L = json.loads((ROOT / "estado/livros_monitoramento.json").read_text(encoding="utf-8"))["ligados"]
        perdidos = [i for i, r in carregar().items() if r.get("decisao") != "D" and i in C and not (C[i].get("parametros") or (L.get(i) or {}).get("parametros"))]
        self.assertEqual(perdidos, [], "livro pesquisado perdeu os parâmetros")

    def test_todo_ligado_tem_livro(self):
        L = json.loads((ROOT / "estado/livros_monitoramento.json").read_text(encoding="utf-8"))["ligados"]
        C = {x["id"] for x in json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]}
        self.assertEqual([k for k in L if k not in C], [])

    def test_curadoria_protege_pesquisado(self):
        for f, trecho in (("src/livros_curadoria.py", 'and not x.get("parametros")'), ("src/livros_repositorio.py", 'x.get("parametros") or not'),
                          ("src/motores.py", 'x.get("parametros") or not')):
            self.assertIn(trecho, (ROOT / f).read_text(encoding="utf-8"), f)

    def test_dados_json_validos(self):
        for f in ("biblioteca_alexandria/fontes/motores.json", "estado/livros_monitoramento.json", "docs/dados/motores.json", "docs/dados/fluxo_oportunidades.json"):
            json.loads((ROOT / f).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
