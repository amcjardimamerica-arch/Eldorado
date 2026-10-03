"""02/10 (titular): estrela do selo (bronze fosca, prata reluzente, ouro cintilante) em cada oportunidade aberta e a
classificação da caixa por Selo Ouro / Prata / Bronze."""
import json, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteSelosNasAbertas(unittest.TestCase):
    def test_estrela_e_do_edital_atual(self):
        """03/10 (titular): bronze = site oficial; prata = + prazo de inscrição; ouro = + os 12 critérios (ou dispensados);
        sem site oficial ou fechada = sem estrela; NÃO herda do livro (o livro tem o seu selo, pelo histórico)."""
        from src import fluxo_oportunidades as F
        doze = {k: {"s": "ok"} for k in json.loads((ROOT / "config/esteira.json").read_text(encoding="utf-8"))["doze_dados"]}
        itens = [{"id": "1", "opressor": "op-l", "url": "https://instituto.org/x"},                           # sem site oficial → sem estrela
                 {"id": "2", "link_oficial": "https://cultura.go.gov.br/e"},                                     # só o site → bronze
                 {"id": "3", "link_oficial": "https://cultura.go.gov.br/e", "fim": "2099-11-30"},                # + prazo → prata
                 {"id": "4", "link_oficial": "https://cultura.go.gov.br/e", "fim": "2099-11-30", "checklist": doze},  # + 12 → ouro
                 {"id": "5", "link_oficial": "https://cultura.go.gov.br/e", "fim": "2020-01-31", "checklist": doze},  # fechada → sem estrela
                 {"id": "6", "url": "https://www.gov.br/cultura/edital"}]                                        # endereço oficial → bronze
        r = F._selos_dos_itens(itens)
        self.assertEqual([i["selo"] for i in itens], [None, "bronze", "prata", "ouro", None, "bronze"])
        self.assertEqual(r, {"bronze": 2, "prata": 1, "ouro": 1})
        self.assertIn("vira histórico do livro", itens[4]["selo_de"])

    def test_painel_estrelas_e_classificacao(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('[["","todas"],["ouro","Selo Ouro"],["prata","Selo Prata"],["bronze","Selo Bronze"]]', h)
        self.assertNotIn('["conf","com prazo e site oficial"],["verif","em verificação"]', h)
        self.assertIn('<span class="oa-selos">${seloEsteira(x)?estrelaSelo(seloEsteira(x)):""}${livroSelo(x.selo_livro)}</span>', h)  # o livro ABAIXO da estrela
        self.assertIn(".oa-selos{display:flex;flex-direction:column", h)
        self.assertIn(".oa-selo.bronze path{fill:#9A6A3C", h)                           # bronze fosco (sem brilho)
        self.assertIn('id="gSeloPrata"', h); self.assertIn("animation:seloOuroBrilho", h)  # prata reluzente; ouro cintilante
        self.assertIn(".oa-selo{width:13px;height:13px", h)                             # estrela pequena
        self.assertIn("prefers-reduced-motion", h)
        self.assertEqual(h.count("function seloDe(id)"), 1); self.assertNotIn("window.seloDe=", h)   # a função antiga continua intacta


if __name__ == "__main__":
    unittest.main()
