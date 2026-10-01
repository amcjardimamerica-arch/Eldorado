"""01/10: regra dos livros — motores regulares levam o checklist ao livro existente e contam os locais de busca; o
Espião cria livro para o que não existe; empresa do Espião entra no ranking só com evidência de apoio."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteRegraDosLivros(unittest.TestCase):
    def test_checklist_vai_ao_livro_e_e_preservado(self):
        from src.livros_regra import anotar_checklist
        from src.livros_opressores import classificar
        x = {"programa": "Edital X", "uf": "GO"}
        self.assertEqual(anotar_checklist(x, {"Objeto": {"v": "apoio a projetos"}, "Valor": "R$ 10 mil"}, "motor teste"), 2)
        classificar(x)
        self.assertEqual(x["livro"]["checklist"]["Valor"]["v"], "R$ 10 mil", "a classificação não pode apagar o checklist")

    def test_espiao_cria_livro_novo(self):
        from src import livros_regra as R
        tmp = Path(tempfile.mkdtemp()) / "cat.json"; shutil.copy(R.CAT, tmp)
        orig = R.CAT; R.CAT = tmp
        try:
            r = R.registrar_achados_do_espiao([{"titulo": "Instituto Teste Unitário abre edital 2026", "url": "https://teste.org.br/edital", "uf": "GO"}])
            self.assertEqual(r["livros_novos"], 1)
            r2 = R.registrar_achados_do_espiao([{"titulo": "Instituto Teste Unitário abre edital 2026", "url": "https://teste.org.br/edital", "uf": "GO"}])
            self.assertEqual(r2["livros_novos"], 0, "o que já existe não vira livro de novo")
        finally:
            R.CAT = orig

    def test_empresa_do_espiao_exige_evidencia(self):
        src = (ROOT / "src/reconhecimento.py").read_text(encoding="utf-8")
        self.assertIn("NAO_EMPRESA", src); self.assertIn("perto = re.search", src)
        from src.reconhecimento import NAO_EMPRESA
        for lixo in ("pizza", "cnpq", "concurso público no exercicio", "órgãos cultura"):
            self.assertTrue(NAO_EMPRESA.search(lixo), lixo)

    def test_locais_de_busca(self):
        d = json.loads((ROOT / "docs/dados/locais_de_busca.json").read_text(encoding="utf-8"))
        self.assertGreater(d["livros"], 500); self.assertIn("livros_atualizados_por_motor", d["hoje"])


if __name__ == "__main__":
    unittest.main()
