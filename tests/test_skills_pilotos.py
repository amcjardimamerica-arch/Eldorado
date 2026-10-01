"""Skills dos Pilotos (29/09): leitura de PDF com expressões em contexto, aprendizado a cada 100 erros, cadastro,
dossiê de empresa, nova ordem do Interceptador e descoberta de entidades novas do Espião."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteSkills(unittest.TestCase):
    def test_busca_expressoes_com_contexto(self):
        from src.skills.leitura_pdf import buscar, trechos_chave
        t = "CRONOGRAMA ... O resultado preliminar será divulgado em 10/11/2026. O prazo para recurso será de 5 dias úteis. Inscrições até 30/10/2026."
        b = buscar(t)
        conds = {x["condicao"] for x in b}
        self.assertIn("Resultado", conds); self.assertIn("Prazo de recurso", conds)
        self.assertTrue(any("10/11/2026" in x["datas"] for x in b if x["condicao"] == "Resultado"))
        self.assertIn("TRECHOS-CHAVE", trechos_chave(t))

    def test_cadastro_distingue_conhecida_de_nova(self):
        from src.skills.cadastro import conhecida
        self.assertTrue(conhecida("Vale S.A."))
        self.assertFalse(conhecida("Instituto Totalmente Novo de Teste 12345"))

    def test_aprendizado_gera_parametros(self):
        P = json.loads((ROOT / "config/parametros_pilotos.json").read_text(encoding="utf-8"))
        self.assertIn("pesos_missao", P.get("espiao", {})); self.assertIn("expressoes_extras", P.get("interceptador", {}))
        from src.skills import aprendizado
        self.assertEqual(aprendizado.LOTE, 100)

    def test_skills_e_carregador(self):
        from src.skills import catalogo, para
        self.assertGreaterEqual(len(catalogo()), 7)
        self.assertLess(len(para("interceptador", "edital")), 2500, "skill carregada não pode inchar o pedido")

    def test_nova_ordem_do_interceptador(self):
        """01/10: a ordem passou a ser guiada pelos livros — Goiás, Brasil, internacional, empresas, outros estados."""
        src = (ROOT / "src/interceptador.py").read_text(encoding="utf-8")
        i = src.index("ORDEM DE BUSCAS GUIADA PELOS LIVROS")
        self.assertLess(src.index('"1 · Goiás"', i), src.index('"4 · empresas · dossiê"', i))
        self.assertLess(src.index('"4 · empresas · dossiê"', i), src.index('"5 · outros estados"', i))

    def test_espiao_descobre_so_o_que_e_novo(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("def missao_descobrir", src); self.assertIn("if conhecida(nome", src)


if __name__ == "__main__":
    unittest.main()
