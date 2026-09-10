"""A ficha de edital tem de nascer em tons claros, como manda a identidade visual.

O caso real: ate 10/09/2026, src/fichas.py trazia a paleta escrita a mao dentro
do codigo — fundo azul-marinho #081426, gradiente #173a5f, texto claro #eaf1f8 —
e com ela gerou as quase dezenove mil fichas do acervo. O arquivo
config/identidade_visual.json diz, na diretriz permanente do titular, "somente
tons claros", e lista "fundo escuro ou modo noturno" entre as proibicoes.

O teste que existia conferia o ARQUIVO de identidade e os arquivos de contexto.
Nenhum conferia o HTML gerado. Regra registrada e nao verificada e regra que o
sistema viola sem que ninguem perceba — o mesmo defeito da curadoria de fontes
apagada pela regeneracao.
"""
import json
import re
import unittest
from pathlib import Path

from src import fichas

ROOT = Path(__file__).resolve().parents[1]
IDENTIDADE = ROOT / "config/identidade_visual.json"

# paleta escura que estava embutida no modulo, com o gradiente do corpo
ESCURAS_ANTIGAS = ("#081426", "#173a5f", "#0d223b", "#0a1b2f", "#eaf1f8", "#244766")


def _luminancia(hexa: str) -> float:
    """Luminancia relativa aproximada, 0 (preto) a 1 (branco)."""
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class TesteFolhaDeEstilo(unittest.TestCase):
    def test_fundo_e_claro(self):
        cores = fichas.paleta()
        for token in ("fundo", "cartao", "realce"):
            self.assertGreater(_luminancia(cores[token]), 0.7,
                               f"{token}={cores[token]} nao e tom claro; "
                               "a diretriz do titular proibe fundo escuro")

    def test_tinta_contrasta_com_o_fundo(self):
        cores = fichas.paleta()
        self.assertLess(_luminancia(cores["tinta"]), 0.35,
                        "texto claro sobre fundo claro nao se le")

    def test_a_paleta_escura_antiga_nao_volta(self):
        folha = fichas.estilo().lower()
        for cor in ESCURAS_ANTIGAS:
            self.assertNotIn(cor.lower(), folha,
                             f"{cor} e da paleta escura removida em 10/09/2026")

    def test_sem_gradiente_escuro_no_corpo(self):
        folha = fichas.estilo()
        corpo = re.search(r"body\{([^}]*)\}", folha)
        self.assertIsNotNone(corpo)
        self.assertNotIn("radial-gradient", corpo.group(1))
        self.assertIn("var(--fundo)", corpo.group(1))

    def test_sem_media_query_de_modo_noturno(self):
        self.assertNotIn("prefers-color-scheme", fichas.estilo())


class TesteFonteUnicaDaIdentidade(unittest.TestCase):
    def test_o_modulo_le_o_arquivo_de_identidade(self):
        fonte = (ROOT / "src/fichas.py").read_text(encoding="utf-8")
        self.assertIn("identidade_visual.json", fonte,
                      "a paleta tem de vir da fonte unica, nao do codigo")

    def test_token_preenchido_no_arquivo_vence_a_paleta_provisoria(self):
        original = json.loads(IDENTIDADE.read_text(encoding="utf-8"))
        try:
            alterado = json.loads(json.dumps(original))
            alterado["tokens"]["cores"]["fundo"] = "#F0EDE6"
            alterado["tokens"]["cores"]["marca_primaria"] = "#3F7D3A"
            IDENTIDADE.write_text(json.dumps(alterado, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
            cores = fichas.paleta()
            self.assertEqual(cores["fundo"], "#F0EDE6")
            self.assertEqual(cores["marca"], "#3F7D3A")
        finally:
            IDENTIDADE.write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")

    def test_token_nulo_cai_na_paleta_clara_provisoria(self):
        cores = fichas.paleta()
        self.assertEqual(cores["fundo"], fichas.PALETA_PROVISORIA["fundo"])


class TesteFichaGerada(unittest.TestCase):
    def test_a_ficha_montada_sai_em_tons_claros(self):
        item = {
            "id": "0000000000000000teste", "titulo": "Chamamento de teste",
            "url": "https://exemplo.gov.br/editais", "fonte_nome": "Fonte de teste",
            "territorio": "GO", "status": "capturada", "evidencia": "trecho literal",
        }
        pagina = fichas.render(item, None)
        self.assertIn("--fundo:#FBFBFA", pagina.replace(" ", ""))
        for cor in ESCURAS_ANTIGAS:
            self.assertNotIn(cor.lower(), pagina.lower())


if __name__ == "__main__":
    unittest.main()
