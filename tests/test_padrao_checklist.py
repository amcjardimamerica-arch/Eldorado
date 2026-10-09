"""10/10 (titular): padrão único de apresentação dos itens conhecidos no checklist das oportunidades abertas.
Ex.: um edital de R$ 40 mil aparecia como "R$ 40". Roda a função do painel no Node (pula se não houver Node)."""
import json, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

CASOS = [
    ("Valor", "Até R$ 40 mil (Mod. 1), R$ 20 mil (Mod. 2)", "até R$ 40.000,00 (+1 valor)"),
    ("Valor", "R$ 40.000,00", "R$ 40.000,00"),
    ("Valor", "40.000,00 reais", "R$ 40.000,00"),
    ("Valor", "R$1.3 milhão", "R$ 1.300.000,00"),
    ("Valor", "até R$ 4,2 milhões", "até R$ 4.200.000,00"),
    ("Valor", "R$ 2,136,760.20 (estimado)", "R$ 2.136.760,20"),
    ("Valor", "mais de R$ 61 milhões", "mais de R$ 61.000.000,00"),
    ("Valor", "Teto de referência EUR 5.000 por apoio", "até € 5.000,00"),
    ("Valor", "Sem dinheiro: associação gratuita", "sem valor em dinheiro"),
    ("Prazo de inscrição", "2026-09-10 a 2026-10-10 23:59", "10/09/2026 a 10/10/2026"),
    ("Prazo de inscrição", "29/09 a 29/10/2026", "29/09/2026 a 29/10/2026"),
    ("Prazo de inscrição", "Prorrogado até 23h59 de 19/10/2026 (DOM 29/09/2026)", "até 19/10/2026"),
    ("Prazo de inscrição", "15 out 2026, 23:59 CEST", "até 15/10/2026"),
    ("Resultado", "2026-12-04", "04/12/2026"),
    ("Prazo de recurso", "05 (cinco) dias úteis", "5 dias úteis"),
    ("Prazo de recurso", "30(trinta)dias", "30 dias"),
    ("Órgão / financiador", "PREFEITURA MUNICIPAL DE SÃO JOSÉ DO VALE DO RIO PRETO", "Prefeitura Municipal de São José do Vale do Rio Preto"),
    ("Órgão / financiador", "MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO", "Minas Gerais Secretaria de Estado da Educação"),
    ("Órgão / financiador", "Municipio deSenadorPompeu!", "Município de Senador Pompeu"),
    ("Território", "nacional", "Nacional"),
    ("Território", "Municipio De Itaitinga / CE", "Itaitinga/CE"),
    ("Território", "go", "GO"),
    ("Esfera", "estadual", "Estadual"),
    ("Área de atuação", "meio_ambiente", "Meio ambiente"),
    ("Anexos", "3 anexo(s)", "3 anexos"),
    ("Anexos", "ANEXO I AMPLA; ANEXO II FORMULÁRIO; ANEXO III DECLARAÇÃO", "3 anexos"),
    ("Destinação", "fora do escopo · premio", "Fora do escopo · prêmio"),
]


@unittest.skipUnless(shutil.which("node"), "Node não disponível")
class TestePadrao(unittest.TestCase):
    def test_padroniza(self):
        s = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        i = s.index("          const MESES="); j = s.index("return frase(v);};", i) + len("return frase(v);};")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(s[i:j] + "\nconst C=" + json.dumps([[k, v] for k, v, _ in CASOS], ensure_ascii=False) +
                    ";\nconsole.log(JSON.stringify(C.map(([k,v])=>padroniza(k,v))));")
        r = subprocess.run(["node", f.name], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for (k, v, esperado), obtido in zip(CASOS, json.loads(r.stdout)):
            self.assertEqual(obtido, esperado, f"{k}: {v!r}")

    def test_o_painel_usa_o_padrao(self):
        s = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('padroniza(k,it.v)', s)
        self.assertNotIn("const curto=(k,v)", s)


if __name__ == "__main__":
    unittest.main()
