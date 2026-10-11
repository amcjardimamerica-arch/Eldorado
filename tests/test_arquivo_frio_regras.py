"""11/10/2026 (titular): páginas de edital órfãs vão ao arquivo frio; PDFs só saem com o Drive conferido; o gerador de
fichas cria páginas só para as oportunidades atuais."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteArquivoFrio(unittest.TestCase):
    def test_conjuntos_novos(self):
        c = {x["nome"]: x for x in json.loads((ROOT / "config/arquivo_frio.json").read_text(encoding="utf-8"))["conjuntos"]}
        self.assertEqual(c["paginas-editais-orfas"]["seletor"], "paginas_editais_orfas")
        self.assertTrue(c["pdfs-documentos-associacao"]["exige_drive"]); self.assertTrue(c["pdfs-anexos-biblioteca"]["exige_drive"])
        self.assertNotIn("dados/farol", json.dumps(c, ensure_ascii=False), "modelos do Farol ficam (o motor de completude os lê)")

    def test_codigo(self):
        a = (ROOT / "src/arquivo_frio.py").read_text(encoding="utf-8")
        self.assertIn('if cj.get("exige_drive") and "drive" not in onde:', a)
        self.assertIn('["git", "ls-files", "-z", cj["padrao"]]', a, "nomes com espaço (PDFs da associação) não podem se partir")
        from src.arquivo_frio import SELETORES
        self.assertIn("paginas_editais_orfas", SELETORES)
        self.assertIn("_vivos = _atuais()", (ROOT / "src/fichas.py").read_text(encoding="utf-8"))

    def test_orfas_nao_incluem_atuais(self):
        from src.arquivo_frio import paginas_editais_orfas
        from src.fichas import _atuais
        vivos = _atuais() or set()
        orfas = {Path(p).stem for p in paginas_editais_orfas()}
        self.assertFalse(orfas & vivos, "nenhuma ficha de oportunidade atual vai para o arquivo frio")


if __name__ == "__main__":
    unittest.main()
