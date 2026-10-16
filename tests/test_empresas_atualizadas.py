"""11/10/2026 (titular): a página de empresas é atual todos os dias — o painel lê o arquivo onde a coleta grava, os
geradores de empresas rodam na rodada diária e as abas mostram a data dos dados."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteEmpresasAtuais(unittest.TestCase):
    def test_arquivo_do_painel_e_o_da_coleta(self):
        from src.empresas import arquivo_do_painel
        a = arquivo_do_painel("GO")
        self.assertEqual(a.parent.name, "go", "o painel lê biblioteca_alexandria/livros/especiais/empresas/go/go.json (o da raiz estava vazio)")
        self.assertIn("from .empresas import arquivo_do_painel", (ROOT / "src/dashboard_dados.py").read_text(encoding="utf-8"))

    def test_rodada_diaria(self):
        w = (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        for m in ("src.catalogo_incentivos", "src.ranking_apoiadores", "src.dossies", "src.radar_piloto", "src.empresas painel GO"):
            self.assertIn(m, w, m)

    def test_datas_nas_abas_e_dossies(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("Dados atualizados em <b>${_quando}</b>", h); self.assertIn("painel atualizado em", h)
        self.assertIn("raw.githubusercontent.com/amcjardimamerica-arch/Eldorado/main/docs/dados/ranking_apoiadores.json", h)
        self.assertIn("if len(feitos) % 5 == 4:", (ROOT / "src/interceptador.py").read_text(encoding="utf-8"))
        self.assertIn("x.get('coletado_em') or 'data não registrada'", (ROOT / "src/dossies.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
