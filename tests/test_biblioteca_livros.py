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
        self.assertIsNotNone(dispensa({"titulo": "Programa de doação da empresa X", "tipo": "empresa/instituto"}))   # 01/10: empresa só como edital
        self.assertIsNone(dispensa({"titulo": "Instituto X abre edital de projetos sociais", "tipo": "empresa/instituto"}))
        self.assertIsNotNone(dispensa({"titulo": "Chamamento público", "orgao": "Prefeitura de Campinas", "uf": "SP"}))   # municipal de outro estado
        self.assertIsNone(dispensa({"titulo": "Chamamento público", "orgao": "Prefeitura de Goiânia", "uf": "GO"}))
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

    def test_cartao_do_livro(self):
        """01/10: Lendo / Na Estante; nome numa linha; lugar com ícone à direita; sem 'Cultura · Grant internacional'."""
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('<option value="ativo">Lendo</option><option value="inativo">Na Estante</option>', h)
        self.assertNotIn("Acesos (automático ou manual)", h); self.assertNotIn("Apagados (poça de óleo)", h)
        self.assertIn("window.lugarLivro=", h); self.assertIn('class="livro-lugar"', h)
        from src.livros_opressores import classificar
        self.assertEqual(classificar({"programa": "PNAB Goiânia - Audiovisual", "uf": "GO"})["municipio"], "Goiânia")

    def test_cada_edital_tem_o_seu_livro(self):
        """01/10: PNAB e outros programas abrem vários editais — objeto, faixa, número (no mesmo ano) ou cidade diferente
        = livros diferentes; edições do mesmo programa em anos diferentes ficam no mesmo livro."""
        from src.curadoria_biblioteca import mesma_oportunidade, editais_distintos
        p = json.loads((ROOT / "config/parametros_biblioteca.json").read_text(encoding="utf-8"))["duplicidade"]
        G = lambda n: {"programa": n, "nome_classificado": n, "geo": "GO", "orgao": "Secult GO", "pagina": "https://goias.gov.br/cultura/"}
        self.assertFalse(mesma_oportunidade(G("PNAB Goiás - Pontos de Cultura"), G("PNAB Goiás - Pontões de Cultura"), p))
        self.assertFalse(mesma_oportunidade(G("Programa Goyazes - projetos de R$ 20 mil a R$ 250 mil"), G("Programa Goyazes - projetos de R$ 250 mil a R$ 2 milhões"), p))
        self.assertFalse(mesma_oportunidade(G("PNAB Goiânia - Dança"), G("PNAB Goiânia - Música"), p))
        self.assertTrue(editais_distintos(G("Edital nº 03/2026 PNAB"), G("Edital nº 04/2026 PNAB")))
        self.assertIsNone(editais_distintos(G("Prêmio X - Edital nº 01/2025"), G("Prêmio X - Edital nº 02/2026")), "edições de anos diferentes")
        self.assertTrue(mesma_oportunidade(G("Edital Ambev 2026: R$ 67M"), G("Edital Ambev 2026: R$ 67M · Capitaai"), p))
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]
        self.assertEqual(sum(1 for x in C if "Goyazes - projetos" in str(x.get("programa"))), 3, "as faixas do Goyazes são livros distintos")


if __name__ == "__main__":
    unittest.main()
