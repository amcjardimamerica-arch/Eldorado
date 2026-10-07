"""02/10 (titular): estrela do selo (bronze fosca, prata reluzente, ouro cintilante) em cada oportunidade aberta e a
classificação da caixa por Selo Ouro / Prata / Bronze."""
import json, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteSelosNasAbertas(unittest.TestCase):
    def test_estrela_e_do_edital_atual(self):
        """04/10 (titular): bronze = objeto + prazo + território; prata = + valor + requisitos; ouro = os 12 validados ou
        dispensados COM justificativa ("não informado" é falta); fechada = sem estrela."""
        from src import fluxo_oportunidades as F
        from src.criterio_selos import DOZE
        base = {"Objeto": {"s": "ok", "v": "Seleção de projetos culturais"}, "Prazo de inscrição": {"s": "val", "v": "01/10 a 30/11/2099"},
                "Território": {"s": "ok", "v": "Goiânia/GO"}}
        prata = {**base, "Valor": {"s": "ok", "v": "R$ 50.000"}, "Requisitos": {"s": "ok", "v": "OSC com 2 anos"}}
        doze = {**prata, **{k: {"s": "ok", "v": "informado no edital"} for k in DOZE if k not in prata}}
        falso = {**doze, "Resultado": {"s": "disp", "v": "não informado no edital"}}
        just = {**doze, "Prazo de recurso": {"s": "disp", "v": "dispensado pelo edital: não há fase de recurso"}}
        itens = [{"id": "1", "checklist": {}, "fim": "2099-11-30"}, {"id": "2", "checklist": base, "fim": "2099-11-30"},
                 {"id": "3", "checklist": prata, "fim": "2099-11-30"}, {"id": "4", "checklist": doze, "fim": "2099-11-30"},
                 {"id": "5", "checklist": falso, "fim": "2099-11-30"}, {"id": "6", "checklist": just, "fim": "2099-11-30"},
                 {"id": "7", "checklist": doze, "fim": "2020-01-31"}]
        F._selos_dos_itens(itens)
        self.assertEqual([i["selo"] for i in itens], [None, "bronze", "prata", "ouro", "prata", "ouro", None])
        self.assertIn("Resultado", itens[4]["selo_faltando"])

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
