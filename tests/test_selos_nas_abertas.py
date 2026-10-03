"""02/10 (titular): estrela do selo (bronze fosca, prata reluzente, ouro cintilante) em cada oportunidade aberta e a
classificação da caixa por Selo Ouro / Prata / Bronze."""
import json, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteSelosNasAbertas(unittest.TestCase):
    def test_cada_quadro_recebe_o_maior_selo(self):
        from src import fluxo_oportunidades as F
        cat = {"motores": [{"id": "op-l", "esteira": {"selo": "prata"}}]}
        doze = {k: {"s": "ok"} for k in json.loads((ROOT / "config/esteira.json").read_text(encoding="utf-8"))["doze_dados"]}
        itens = [{"id": "1", "opressor": "op-l", "url": "https://instituto.org/x"},                       # livro prata, quadro bronze → prata
                 {"id": "2", "url": "https://instituto.org/y"},                                              # sem livro, sem site oficial → bronze
                 {"id": "3", "opressor": "op-l", "link_oficial": "https://cultura.go.gov.br/e", "fim": "2026-11-30", "checklist": doze}]  # quadro ouro
        real = Path.read_text
        def ler(p, *a, **k):
            return json.dumps(cat) if str(p).endswith("fontes/motores.json") else real(p, *a, **k)
        with mock.patch.object(Path, "read_text", ler):
            r = F._selos_dos_itens(itens)
        self.assertEqual([i["selo"] for i in itens], ["prata", "bronze", "ouro"]); self.assertEqual(r, {"prata": 1, "bronze": 1, "ouro": 1})
        self.assertIn('"selo", "selo_de"', (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))

    def test_painel_estrelas_e_classificacao(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('[["","todas"],["ouro","Selo Ouro"],["prata","Selo Prata"],["bronze","Selo Bronze"]]', h)
        self.assertNotIn('["conf","com prazo e site oficial"],["verif","em verificação"]', h)
        self.assertIn("${estrelaSelo(seloEsteira(x))}${livroSelo(x.selo_livro)}</div>", h)   # 03/10: estrela + livro                       # canto direito da 1ª linha
        self.assertIn(".oa-selo.bronze path{fill:#9A6A3C", h)                           # bronze fosco (sem brilho)
        self.assertIn('id="gSeloPrata"', h); self.assertIn("animation:seloOuroBrilho", h)  # prata reluzente; ouro cintilante
        self.assertIn(".oa-selo{width:13px;height:13px", h)                             # estrela pequena
        self.assertIn("prefers-reduced-motion", h)
        self.assertEqual(h.count("function seloDe(id)"), 1); self.assertNotIn("window.seloDe=", h)   # a função antiga continua intacta


if __name__ == "__main__":
    unittest.main()
