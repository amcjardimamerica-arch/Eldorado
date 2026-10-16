"""11/10/2026 (titular): redução de espaço sem perda — backup, arquivo frio dos conjuntos sem uso, logs regeneráveis
fora do Git, e os Pilotos regeneram o painel no máximo a cada 30 min (o histórico crescia ~155 MB em 3 dias só por isso)."""
import json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteReducao(unittest.TestCase):
    def test_arquivo_frio_e_logs(self):
        c = {x["nome"] for x in json.loads((ROOT / "config/arquivo_frio.json").read_text(encoding="utf-8"))["conjuntos"]}
        for n in ("validacao-abertas-sem-ouro-2026-10-03", "coleta-3-anos-relatorios-oportunidades", "contagens-anteriores-pilotos"):
            self.assertIn(n, c)
        self.assertIn("biblioteca_alexandria/livros/especiais/espiao/servidor-*.log", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_painel_dos_pilotos_a_cada_30_min(self):
        w = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn('if [ "${IDADE_PAINEL}" -ge 30 ]; then', w)
        i = w.index("IDADE_PAINEL=$("); j = w.index("timeout 300 python -m src.dashboard_dados", i)
        self.assertLess(i, j, "o gerador do painel fica dentro da condição dos 30 min")
        self.assertTrue((ROOT / "docs/prompts/PROMPT-REDUCAO-ESPACO-2026-10-11.md").exists())


if __name__ == "__main__":
    unittest.main()
