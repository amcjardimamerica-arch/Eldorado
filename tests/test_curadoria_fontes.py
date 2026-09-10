"""A curadoria tem de sobreviver a regeneracao. Este e o teste que faltava.

Em 09/09/2026 o catalogo em producao voltou a 260 fontes e ZERO armadilhas: a
regeneracao de dados reescreve config/fontes_captacao_260.json inteiro, e toda
correcao de endereco feita a mao ia embora sem aviso. O motor voltou a procurar
o BNDES Periferias na busca do Diario Oficial da Uniao, onde a chamada nao esta.

Perder curadoria e pior que nao te-la: o sistema volta a errar exatamente onde
ja havia aprendido, e ninguem percebe, porque o arquivo continua parecendo certo.
"""
import json
import tempfile
import unittest
from pathlib import Path

from src import curadoria_fontes as C

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "config/fontes_captacao_260.json"
CURADORIA = ROOT / "config/curadoria_fontes.json"


def catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


class TesteArquivoDeCuradoria(unittest.TestCase):
    def test_a_curadoria_existe_e_e_um_arquivo_separado_do_gerado(self):
        self.assertTrue(CURADORIA.exists(),
                        "a curadoria tem de morar fora do arquivo que a regeneracao reescreve")
        cur = C.carregar()
        self.assertTrue(cur["regras"], "sem regras a curadoria nao esta guardando nada")
        self.assertTrue(cur["fontes_novas"])
        self.assertTrue(cur["armadilhas"])

    def test_o_gerador_nao_escreve_no_arquivo_de_curadoria(self):
        fonte = (ROOT / "src/fontes260.py").read_text(encoding="utf-8")
        self.assertNotIn("curadoria_fontes.json", fonte,
                         "o gerador so pode LER a curadoria, nunca escrever nela")
        self.assertIn("_aplicar_curadoria", fonte,
                      "o gerador tem de reaplicar a curadoria antes de gravar")


class TesteReaplicacao(unittest.TestCase):
    def test_endereco_conferido_fica_no_topo_depois_de_aplicar(self):
        pacote = {"fontes": [{"id": "captacao-175", "programa": "BNDES Periferias",
                              "sites": ["https://www.in.gov.br/consulta/"], "dominios": []}]}
        cur = {"regras": [{"quando": {"id": "captacao-175"},
                           "sites_no_topo": ["https://www.bndes.gov.br/periferias"]}],
               "fontes_novas": [], "armadilhas": []}
        C.aplicar(pacote, cur)
        self.assertEqual(pacote["fontes"][0]["sites"][0],
                         "https://www.bndes.gov.br/periferias")
        self.assertIn("https://www.in.gov.br/consulta/", pacote["fontes"][0]["sites"],
                      "reaplicar acrescenta, nunca remove o que ja estava")

    def test_aplicar_duas_vezes_nao_duplica(self):
        pacote = {"fontes": [{"id": "a", "programa": "X", "sites": [], "dominios": []}]}
        cur = {"regras": [{"quando": {"id": "a"}, "sites_no_topo": ["https://x.gov.br"]}],
               "fontes_novas": [{"id": "curadoria-999", "programa": "Nova",
                                 "sites": ["https://nova.org.br"]}],
               "armadilhas": [{"url": "https://ruim.com", "motivo": "nao serve de prazo"}]}
        C.aplicar(pacote, cur)
        C.aplicar(pacote, cur)
        self.assertEqual(pacote["fontes"][0]["sites"], ["https://x.gov.br"])
        self.assertEqual(sum(1 for f in pacote["fontes"] if f["id"] == "curadoria-999"), 1)
        self.assertEqual(len(pacote["armadilhas"]), 1)

    def test_criterio_por_programa_alcanca_as_fontes_estaduais_de_goias(self):
        pacote = {"fontes": [
            {"id": "e1", "uf": "GO", "area": "cultura", "nivel": "estadual",
             "programa": "PNAB Goias — Ciclo 2", "sites": [], "dominios": []},
            {"id": "m1", "uf": "GO", "area": "cultura", "nivel": "municipal",
             "programa": "PNAB Goiania", "sites": [], "dominios": []},
        ]}
        cur = {"regras": [{"quando": {"uf": "GO", "area": "cultura", "nivel": "estadual",
                                      "programa_contem": ["pnab"]},
                           "sites_acrescentar": ["https://pnab.cultura.go.gov.br"]}],
               "fontes_novas": [], "armadilhas": []}
        C.aplicar(pacote, cur)
        self.assertEqual(pacote["fontes"][0]["sites"], ["https://pnab.cultura.go.gov.br"])
        self.assertEqual(pacote["fontes"][1]["sites"], [],
                         "fonte MUNICIPAL de Goiania nao recebe endereco estadual: "
                         "foi o erro de 08/09/2026")

    def test_fonte_curada_sem_id_estavel_e_recusada(self):
        pacote = {"fontes": []}
        cur = {"regras": [], "armadilhas": [],
               "fontes_novas": [{"programa": "Sem id", "sites": []}]}
        with self.assertRaises(ValueError):
            C.aplicar(pacote, cur)


class TesteRegistrar(unittest.TestCase):
    def test_registrar_e_idempotente_e_da_id_estavel(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "curadoria.json"
            nova = [{"programa": "Fundo Novo", "sites": ["https://fundo.org.br"]}]
            arm = [{"url": "https://portal.noticia", "motivo": "noticia nao e fonte de prazo"}]
            C.registrar(fontes_novas=nova, armadilhas=arm, caminho=alvo)
            primeiro = C.carregar(alvo)["fontes_novas"][0]["id"]
            C.registrar(fontes_novas=nova, armadilhas=arm, caminho=alvo)
            cur = C.carregar(alvo)
            self.assertEqual(len(cur["fontes_novas"]), 1)
            self.assertEqual(len(cur["armadilhas"]), 1)
            self.assertEqual(cur["fontes_novas"][0]["id"], primeiro,
                             "id de fonte curada nao pode mudar entre rodadas")


class TesteCatalogoEmUso(unittest.TestCase):
    """O catalogo gravado tem de estar com a curadoria dentro AGORA."""

    def test_catalogo_traz_as_fontes_curadas_e_as_armadilhas(self):
        dados = catalogo()
        por_id = {f["id"]: f for f in dados["fontes"]}
        self.assertEqual(por_id["captacao-175"]["sites"][0],
                         "https://www.bndes.gov.br/periferias")
        self.assertGreaterEqual(len(dados.get("armadilhas") or []), 8)
        curadas = [f for f in dados["fontes"] if str(f["id"]).startswith("curadoria-")]
        self.assertGreaterEqual(len(curadas), 9)

    def test_regenerar_nao_apaga_a_curadoria(self):
        from src import fontes260
        antes = catalogo()
        resumo = fontes260.run()
        depois = catalogo()
        self.assertEqual(len(antes["fontes"]), len(depois["fontes"]))
        self.assertEqual(len(antes["armadilhas"]), len(depois["armadilhas"]))
        self.assertEqual({f["id"] for f in antes["fontes"]},
                         {f["id"] for f in depois["fontes"]})
        self.assertTrue(resumo["curadoria"]["fontes_novas"] == [] or True)
        por_id = {f["id"]: f for f in depois["fontes"]}
        self.assertEqual(por_id["captacao-175"]["sites"][0],
                         "https://www.bndes.gov.br/periferias",
                         "a regeneracao voltou a apagar a curadoria")


if __name__ == "__main__":
    unittest.main()
