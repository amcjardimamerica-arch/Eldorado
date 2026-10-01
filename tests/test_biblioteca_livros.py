"""01/10: Motores Opressores viram a BIBLIOTECA — livros de oportunidades e de leis; Interceptador guiado pelos livros."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteBiblioteca(unittest.TestCase):
    def test_nome_do_livro(self):
        from src.livros_opressores import classificar
        self.assertEqual(classificar({"programa": "Edital PNAB Dança", "uf": "SP"})["nome_classificado"], "Edital PNAB Dança — São Paulo")
        d = classificar({"programa": 'Diário Oficial de Campinas (SP) 2026-07-31 — "chamamento público" OSC', "uf": "SP",
                         "historico": [{"titulo": "Diário Oficial de Campinas (SP)", "uf": "SP"}]})
        self.assertEqual(d["nome_classificado"], "Chamamento público publicado no Diário Oficial em 31/07/2026 — São Paulo / Campinas")

    def test_toda_oportunidade_vira_livro(self):
        from src.opressores_repositorio import dispensa
        self.assertIsNone(dispensa({"titulo": "Emenda parlamentar estadual 2026"}))
        self.assertIsNone(dispensa({"titulo": "Programa de doação da empresa X", "tipo": "empresa/instituto"}))
        self.assertIsNotNone(dispensa({"titulo": "Dispensa de chamamento público nº 3"}))

    def test_livro_sem_arquivo_e_enxuto(self):
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]
        for x in C[:300]:
            self.assertFalse(any(k in x for k in ("pdf", "arquivo", "arquivos", "anexo_binario", "base64")))
            self.assertNotIn("geografia", x.get("livro") or {}, "o livro não repete o que já está no registro")

    def test_livros_de_leis(self):
        from src.livros_leis import montar
        r = montar(); self.assertGreaterEqual(r["livros_de_leis"], 20); self.assertEqual(r["sem_oportunidade"], 0)

    def test_ordem_do_interceptador(self):
        src = (ROOT / "src/interceptador.py").read_text(encoding="utf-8")
        i = src.index("ORDEM DE BUSCAS GUIADA PELOS LIVROS")
        pos = [src.index(s, i) for s in ('"1 · Goiás"', '"2 · Brasil"', '"3 · internacional aplicável ao Brasil"', '"4 · empresas · dossiê"', '"5 · outros estados"')]
        self.assertEqual(pos, sorted(pos))

    def test_painel_biblioteca(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn(">Biblioteca", h); self.assertIn("window.desenhaLeis=", h); self.assertIn("repeat(2,minmax(0,1fr))", h)
        import re
        self.assertNotIn("Motores Opressores", h); self.assertNotIn("motores opressores", h)


if __name__ == "__main__":
    unittest.main()
