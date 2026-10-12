"""12/10/2026 (titular): cartões sem botões; clicar abre a FICHA da oportunidade (achado, esteira, sistemas, livro) com
as ações dentro dela; descartar não apaga o livro — sinaliza para o Claude analisar a exclusão."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteFicha(unittest.TestCase):
    def setUp(self):
        self.h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        i = self.h.index("function _desenhaAbertasFluxo(){"); self.card = self.h[i:self.h.index("cx.innerHTML=", i)]

    def test_cartao_sem_botoes_e_clique_abre_a_ficha(self):
        self.assertNotIn('class="bt-insc"', self.card); self.assertNotIn('class="acoes-ed"', self.card)
        self.assertIn("fichaOportunidade(x)", self.h)

    def test_ficha_tem_as_secoes_e_as_acoes_dentro(self):
        for marca in ('"Como foi encontrada"', '"Esteira · o que foi feito e o que falta"', '"Sistemas que já averiguaram"', '"Livro da oportunidade"',
                      'id="fo-insc"', 'id="fo-desc"', 'id="fo-ia"', 'id="fo-exp"', 'id="fo-rec"', "descartarOportunidade(e)", "O livro não é apagado"):
            self.assertIn(marca, self.h, marca)

    def test_gerador_das_fichas(self):
        from src import fichas_oportunidades as F
        r = F.montar(); self.assertGreater(r["total"], 0)
        f = next(iter(r["fichas"].values()))
        for k in ("achado", "esteira", "sistemas", "livro"):
            self.assertIn(k, f)
        self.assertEqual({s["sistema"] for s in f["sistemas"]} >= {"Motores (coleta)", "Rede neural", "Cartório", "Interceptador"}, True)

    def test_descarte_sinaliza_o_livro_sem_apagar(self):
        from src import decisoes_titular as D
        t = Path(tempfile.mkdtemp()); shutil.copy(D.CATALOGO, t / "c.json")
        o = (D.CATALOGO, D.DECISOES, D.FILA)
        try:
            D.CATALOGO, D.DECISOES, D.FILA = t / "c.json", t / "d.json", t / "f.json"
            R = json.loads(D.REP.read_text(encoding="utf-8"))["registros"]; r = next(x for x in R if x.get("livro") and x["estado"] != "fechada")
            D.DECISOES.write_text(json.dumps({"decisoes": {r["id"]: {"estado": "descartado", "em": "2026-10-12T10:00:00Z"}}}))
            D.run(); L = next(m for m in json.loads(D.CATALOGO.read_text())["motores"] if m["id"] == r["livro"])
            self.assertEqual(L["revisao_exclusao"]["situacao"], "aguardando análise do Claude", "o livro fica, com o sinalizador")
            self.assertIn("aguardando análise do Claude", D.marca_no_repositorio([r["id"]], D.decisoes()))
            D.DECISOES.write_text(json.dumps({"decisoes": {}})); D.run()
            L = next(m for m in json.loads(D.CATALOGO.read_text())["motores"] if m["id"] == r["livro"])
            self.assertNotIn("revisao_exclusao", L, "recuperada: o sinalizador sai")
        finally:
            D.CATALOGO, D.DECISOES, D.FILA = o

    def test_nos_fluxos(self):
        w = (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.fichas_oportunidades", w); self.assertIn("python -m src.decisoes_titular", w)
        self.assertIn("python -m src.decisoes_titular", (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
