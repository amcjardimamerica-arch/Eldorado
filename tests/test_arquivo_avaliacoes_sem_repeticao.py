"""09/10: o arquivo mensal de avaliações do Espião tinha cada avaliação ~200 vezes (out/2026: 1.397.115 linhas para
6.872). A faxina reanexava os .json que o pouso dos voos recolocava. Agora não repete, e a leitura é em fluxo."""
import json, lzma, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteArquivoSemRepeticao(unittest.TestCase):
    def test_leitura_sem_repeticao(self):
        from src import aprendizados_piloto as A
        with tempfile.TemporaryDirectory() as t:
            T = Path(t); arq = T / "arquivo-2026-10.jsonl.xz"
            linhas = [json.dumps({"arquivo": f"a{i % 3}.json", "avaliacao": {"em": f"2026-10-0{1 + i % 3}T12:00:00+00:00"}}) for i in range(30)]
            arq.write_bytes(lzma.compress(("\n".join(linhas) + "\n").encode()))
            self.assertEqual(len(A.avaliacoes_arquivadas(T)), 3)
            self.assertEqual(len(A.avaliacoes_arquivadas(T, desde="2026-11-01T00:00:00+00:00")), 0)
            self.assertEqual([n for _l, n in A.linhas_unicas(arq)], ["a0.json", "a1.json", "a2.json"])

    def test_faxina_nao_reanexa(self):
        s = (ROOT / "src/aprendizados_piloto.py").read_text(encoding="utf-8")
        self.assertIn('novas = [x for x in linhas if x["arquivo"] not in ja]', s)

    def test_leitores_usam_o_leitor_sem_repeticao(self):
        for f in ("src/espiao_relatorio.py", "src/skills/aprendizado.py"):
            s = (ROOT / f).read_text(encoding="utf-8")
            self.assertIn("avaliacoes_arquivadas", s, f); self.assertNotIn("lzma.decompress(Path(f).read_bytes())", s, f)


if __name__ == "__main__":
    unittest.main()
