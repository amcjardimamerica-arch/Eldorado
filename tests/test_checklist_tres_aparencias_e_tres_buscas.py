"""09/10 (titular): no checklist das oportunidades abertas, o item CONHECIDO mostra a informação confirmada no lugar do
nome (✓ verde forte), o DISPENSADO fica azul e o resto é ✕ vermelho (sem o ponto cinza); o Interceptador e o Cartório
buscam cada oportunidade até 3 vezes."""
import json, sys, tempfile, unittest
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePainel(unittest.TestCase):
    def test_tres_aparencias_e_informacao_no_lugar_do_nome(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('.oa-ki.conhecido i{background:#1E7E4B', h, "um só verde, o forte (titular, 09/10)")
        self.assertNotIn('.oa-ki.conhecido i{background:#8FC9A3', h, "sem o verde claro")
        self.assertIn(".oa-ki.disp i{background:#2F79D0", h, "dispensado em azul")
        self.assertIn(".oa-ki.buscar i{background:#FBE3E1;color:#B3261E}", h, "✕ vermelho")
        self.assertNotIn(".oa-ki.pend", h, "sem o ponto cinza"); self.assertNotIn('pend:"·"', h)
        self.assertIn('rot=g==="conhecido"&&it.v?curto(k,it.v):k', h, "a informação confirmada substitui o nome")
        self.assertIn("até 3 vezes por oportunidade", h)


class TesteInterceptador(unittest.TestCase):
    def setUp(self):
        from src import interceptador as I
        self.I = I; self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.orig = {k: getattr(I, k) for k in ("ESTADO", "FILA", "_itens_em_x", "registro")}
        I.ESTADO = T / "estado.json"; I.FILA = T / "fila.json"
        I.registro = lambda eid: {"titulo": "edital"} if eid.startswith("x") else None
        velho = (date.today() - timedelta(days=5)).isoformat() + "T10:00:00+00:00"
        hoje = date.today().isoformat() + "T10:00:00+00:00"
        I.ESTADO.write_text(json.dumps({"feitos": {"x1": {"em": velho}, "x2": {"em": velho, "buscas": 3},
                                                   "x3": {"em": hoje, "buscas": 1}, "x4": {"em": velho, "buscas": 2}}}))
        I._itens_em_x = lambda: {k: {"x": 3, "titulo": k, "fim": "2026-12-01"} for k in ("x1", "x2", "x3", "x4")}

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(self.I, k, v)
        self.tmp.cleanup()

    def test_revisita_ate_a_terceira_busca(self):
        ids = {a["id"]: a["de"] for a in self.I.alvos(400)}
        self.assertIn("x1", ids); self.assertIn("busca 2 de 3", ids["x1"])
        self.assertIn("x4", ids); self.assertIn("busca 3 de 3", ids["x4"])
        self.assertNotIn("x2", ids, "já buscou 3 vezes")
        self.assertNotIn("x3", ids, "buscou hoje: espera 2 dias")

    def test_contagem_das_buscas(self):
        est = {"feitos": {"a": {"em": "x"}}}
        self.assertEqual(self.I._com_buscas(est, "a", {})["buscas"], 2, "registro antigo sem contagem vale 1")
        self.assertEqual(self.I._com_buscas(est, "novo", {})["buscas"], 1)


class TesteCartorio(unittest.TestCase):
    def test_tres_tentativas_salvo_informacao_nova(self):
        from src import cartorio as C
        op = {"id": "e1", "_tipo": "estrela", "_faltam": ["Valor"], "url": "https://x.go.gov.br/a"}
        cert = {"tentativa": 3, "assinatura": C._assinatura(op), "em": "2000-01-01", "versao": "antiga", "ainda_faltam": ["Valor"]}
        self.assertEqual(C.devidos([op], {"estrela:e1": cert}, 7), [], "3ª tentativa feita: para")
        op2 = {**op, "url_documento": "https://x.go.gov.br/edital-novo.pdf"}
        self.assertEqual(len(C.devidos([op2], {"estrela:e1": cert}, 7)), 1, "informação nova dos motores reabre")
        self.assertEqual(len(C.devidos([op], {"estrela:e1": {**cert, "tentativa": 2}}, 7)), 1)


if __name__ == "__main__":
    unittest.main()
