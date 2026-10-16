"""11/10/2026 (titular): parâmetro único — abertas = validadas + em verificação + validação manual; fechadas por
veredito e prazos vencidos ficam fora; a tela inicial usa o mesmo número."""
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.fluxo_oportunidades import aplicar_parametro


class TesteParametro(unittest.TestCase):
    def test_estados_e_exclusoes(self):
        itens = [{"id": "a", "confirmada": True, "fim": "2026-12-01"}, {"id": "b"}, {"id": "c"}, {"id": "d"}, {"id": "e", "fim": "2026-01-01"}, {"id": "f"}]
        ver = {"b": {"veredito": "ouro"}, "c": {"veredito": "validacao_manual"}, "d": {"veredito": "ruido"}}
        ab, p = aplicar_parametro(itens, ver, "2026-10-11")
        self.assertEqual({x["id"]: x["estado"] for x in ab}, {"a": "validada", "b": "validada", "c": "validacao_manual", "f": "em_verificacao"})
        self.assertEqual((p["abertas"], p["validadas"], p["em_verificacao"], p["validacao_manual"]), (4, 2, 1, 1))
        self.assertEqual(p["abertas"], p["validadas"] + p["em_verificacao"] + p["validacao_manual"])
        self.assertEqual(p["fora_do_parametro"], {"fechada por veredito": 1, "prazo vencido": 1})

    def test_tela_inicial_usa_o_parametro(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('const PR=FX.parametro||', h); self.assertIn('"Oportunidades abertas",`${PR.abertas}`', h)
        self.assertIn('fr(PR.validadas,PR.abertas)', h)


if __name__ == "__main__":
    unittest.main()


class TesteUmUniverso(unittest.TestCase):
    """11/10: a lista do fluxo (tela inicial) e o repositório (Bússola) têm o mesmo universo."""
    def test_lista_segue_o_repositorio(self):
        import tempfile, json as _json
        from src import fluxo_oportunidades as F
        rep = {"registros": [{"id": "a", "ids_origem": ["a", "a2"], "estado": "em_verificacao", "itens": {}},
                             {"id": "b", "ids_origem": ["b"], "estado": "fechada", "itens": {}},
                             {"id": "c", "ids_origem": ["c"], "estado": "validada", "uf": "GO", "titulo": "só da caixa", "itens": {"Objeto": {"estado": "comprovado", "valor": "x"}}}]}
        res = {"itens_por_uf": {"GO": [{"id": "a"}, {"id": "a2"}, {"id": "b"}]}}
        with tempfile.TemporaryDirectory() as t:
            orig = F.ROOT; F.ROOT = Path(t)
            (Path(t) / "biblioteca_alexandria/livros/_vistas").mkdir(parents=True)
            (Path(t) / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json").write_text(_json.dumps(rep))
            try:
                n = F.incluir_do_repositorio(res)
            finally:
                F.ROOT = orig
        ids = [x["id"] for L in res["itens_por_uf"].values() for x in L]
        self.assertEqual(sorted(ids), ["a", "c"], "duplicata e fechada saem; a que só o repositório tinha entra")
        self.assertEqual(n, 1)
