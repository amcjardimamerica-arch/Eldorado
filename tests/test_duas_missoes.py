"""As duas missões do Piloto, como o titular definiu (23/09)."""
import json, pathlib, unittest
from src.missao_especial import _e_pncp, montar_fila, PARA_O_CLAUDE, registrar_resgate
from src.reconhecimento import (ler_rastros, registrar, proximo_do_plano, publicar,
                                FRENTES, VIAS, NAO_E_EMPRESA)
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteMissao1_PNCPForaDoPiloto(unittest.TestCase):
    """PNCP é dado genérico de compras públicas: quem analisa é o Claude, por fora."""

    def test_reconhece_pncp_em_qualquer_campo(self):
        self.assertTrue(_e_pncp({"origem": "acervo PNCP/motores"}))
        self.assertTrue(_e_pncp({"titulo": "[Portal de Compras Públicas] - Credenciamento"}))
        self.assertTrue(_e_pncp({"url": "https://pncp.gov.br/app/editais/123"}))
        self.assertFalse(_e_pncp({"titulo": "Edital Secult", "url": "https://goias.gov.br/x"}))

    def test_pncp_vai_para_a_fila_do_claude(self):
        r = montar_fila()
        self.assertGreater(r["para_o_claude"], 300)
        d = json.loads(PARA_O_CLAUDE.read_text(encoding="utf-8"))
        self.assertIn("o Piloto não toca PNCP", d["regra"])
        self.assertIn("Claude Desktop", d["regra"])
        self.assertTrue(all(v.get("porque") for v in d["itens"].values()))
        # e nada de PNCP sobra na fila do Piloto
        f = json.loads((ROOT / "estado/piloto/fila_resgate.json").read_text(encoding="utf-8"))
        for v in f["itens"].values():
            if v.get("estado") == "aguardando":
                self.assertFalse(_e_pncp(v), v.get("titulo"))

    def test_uma_unica_vez(self):
        src = (ROOT / "src/missao_especial.py").read_text(encoding="utf-8")
        self.assertIn("UMA ÚNICA VEZ", src)
        self.assertIn('tentados.get(e["id"], 0) >= 1', src)
        self.assertIn("entregue_ao_claude", src)
        self.assertIn("daria o mesmo nada", src)


class TesteMissao2_Reconhecimento(unittest.TestCase):
    """A pergunta não é que edital está aberto: é quem pagou pelo que já aconteceu."""

    def test_le_quem_pagou_e_por_qual_via(self):
        t = ("O projeto teve patrocínio da Agroluz Alimentos e contou com o apoio da Construtora "
             "Meridiano. A quadra foi viabilizada pelo Instituto Bandeirante, com recursos da Lei "
             "de Incentivo ao Esporte. A doação de cestas foi feita pelo Supermercado Cerrado. "
             "O evento teve realização da Fundação Vale Verde e apoio institucional do Banco Meridiano.")
        r = ler_rastros(t, "https://jornal.com.br/m")
        nomes = [x["empresa"] for x in r]
        for esperado in ("Agroluz Alimentos", "Construtora Meridiano", "Instituto Bandeirante",
                         "Supermercado Cerrado", "Fundação Vale Verde", "Banco Meridiano"):
            self.assertIn(esperado, nomes, esperado)
        vias = {x["empresa"]: x["via"] for x in r}
        self.assertEqual(vias["Instituto Bandeirante"], "incentivo_fiscal")   # a lei manda na via
        self.assertEqual(vias["Supermercado Cerrado"], "doacao")

    def test_lei_nao_e_empresa(self):
        self.assertTrue(NAO_E_EMPRESA.search("Lei de Incentivo ao Esporte"))
        self.assertTrue(NAO_E_EMPRESA.search("Prefeitura Municipal"))
        self.assertFalse(NAO_E_EMPRESA.search("Agroluz Alimentos"))

    def test_as_quatro_frentes_e_as_cinco_vias(self):
        self.assertEqual(set(FRENTES), {"entidade", "imprensa", "evento", "prestacao"})
        for k, f in FRENTES.items():
            self.assertTrue(f["rotulo"] and f["procurar"] and f["onde_olhar"] and f["rende"], k)
        self.assertEqual(set(VIAS), {"patrocinio", "doacao", "incentivo_fiscal",
                                     "marketing_social", "convenio"})

    def test_cada_descoberta_altera_o_plano_de_voo(self):
        registrar({"empresa": "Teste Reconhecimento SA", "via": "patrocinio",
                   "trecho": "patrocínio da Teste", "onde_vi": "https://x.org"}, "imprensa", "regional")
        p = proximo_do_plano()
        self.assertTrue(p)
        self.assertIn("financia no terceiro setor", p["pergunta"])
        self.assertGreaterEqual(len(p["a_investigar"]), 5)
        pub = publicar()
        self.assertGreaterEqual(pub["no_plano_de_voo"], 1)
        self.assertIn("não houve edital publicado", pub["porque_os_motores_nao_acham"])

    def test_a_missao_esta_no_voo(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("def missao_reconhecimento", src)
        self.assertIn("proximo_do_plano", src)                 # o plano manda primeiro
        self.assertIn("Não procura edital: procura ATIVIDADE JÁ FEITA", src)
        self.assertIn("missao_reconhecimento(ia,", src)


class TesteCargoDeclaraAsDuas(unittest.TestCase):
    def test_o_cargo_descreve_as_duas_missoes(self):
        c = json.loads((ROOT / "config/cargo_piloto.json").read_text(encoding="utf-8"))
        f = c["finalidade"]
        self.assertIn("missao_1_especial", f); self.assertIn("missao_2_regular", f)
        self.assertIn("PNCP", f["missao_1_especial"]["nao_toca"])
        self.assertIn("Claude Desktop", f["missao_1_especial"]["nao_toca"])
        self.assertIn("UMA UNICA VEZ", f["missao_1_especial"]["o_que"])
        self.assertIn("QUEM PAGOU", f["missao_2_regular"]["o_que"])
        self.assertGreaterEqual(len(f["missao_2_regular"]["vias_procuradas"]), 5)
        self.assertIn("altera_o_plano_de_voo", f["missao_2_regular"])


class TesteExtracaoComFrasesDificeis(unittest.TestCase):
    """O conselho pediu frases adversariais: os quatro defeitos de 23/09 eram todos de leitura
    de texto e passariam despercebidos em produção, porque produziriam nomes certos com vias
    erradas — e ninguém olharia."""

    def _vias(self, texto):
        return {x["empresa"]: x["via"] for x in ler_rastros(texto, "https://t.org/x")}

    def test_a_via_nao_vaza_da_frase_vizinha(self):
        v = self._vias("O evento teve apoio da Construtora Meridiano. A quadra foi viabilizada "
                       "pelo Instituto Raiz, com recursos da Lei de Incentivo ao Esporte.")
        self.assertEqual(v["Construtora Meridiano"], "patrocinio")     # não herda do vizinho
        self.assertEqual(v["Instituto Raiz"], "incentivo_fiscal")

    def test_ponto_final_nao_entra_no_nome(self):
        v = self._vias("Teve patrocínio da Alfa Meridiano. A entidade agradece.")
        self.assertIn("Alfa Meridiano", v)
        self.assertNotIn("Alfa Meridiano. A", str(v))

    def test_abreviatura_sobrevive(self):
        r = ler_rastros("O projeto teve patrocínio da Alfa S.A e apoio do Banco Beta.", "https://t.org")
        nomes = [x["empresa"] for x in r]
        self.assertTrue(any(n.startswith("Alfa") for n in nomes), nomes)
        self.assertIn("Banco Beta", nomes)

    def test_lei_por_extenso_define_a_via(self):
        """A matéria escreve o nome inteiro; a lista dizia só a sigla."""
        for texto, esperado in (
                ("financiado pela Cimento Araguaia através do Fundo do Idoso.", "incentivo_fiscal"),
                ("financiado pela Usina Boa Vista pelo Fundo da Criança e do Adolescente.", "incentivo_fiscal"),
                ("patrocinado pela Rede Norte com renúncia fiscal do município.", "incentivo_fiscal"),
                ("doação da Padaria Central para a campanha.", "doacao")):
            v = self._vias(texto)
            self.assertEqual(list(v.values())[0], esperado, texto)

    def test_dois_creditos_na_mesma_frase(self):
        v = self._vias("Realização da Fundação Alfa e apoio institucional do Banco Beta.")
        self.assertEqual(set(v), {"Fundação Alfa", "Banco Beta"})

    def test_caixa_alta_no_credito(self):
        r = ler_rastros("PATROCÍNIO DA AGROLUZ ALIMENTOS. Evento gratuito.", "https://t.org")
        self.assertTrue(any("AGROLUZ" in x["empresa"] for x in r), [x["empresa"] for x in r])

    def test_nao_confunde_orgao_publico_com_empresa(self):
        r = ler_rastros("Com apoio da Prefeitura Municipal de Anápolis e da Secretaria de Cultura.",
                        "https://t.org")
        self.assertEqual(r, [], [x["empresa"] for x in r])


class TesteAprendizadoDoReconhecimento(unittest.TestCase):
    """O crivo foi escrito para edital: exige prazo e inscrição, que um financiador não tem.
    Sem ramo próprio, todo voo de reconhecimento bem-sucedido marcava efetividade zero."""

    class _Mudo:
        def perguntar(self, p, e=None): return None

    def test_financiador_nomeado_com_prova_conta_como_util(self):
        from src.aprendizados_piloto import avaliar
        r = avaliar(self._Mudo(), {"motor": "sindico-aberto", "tipo": "reconhecimento", "licao": "x"},
                    [{"titulo": "Agroluz Alimentos", "url": "https://j.com",
                      "trecho": "patrocínio da Agroluz Alimentos no projeto", "confirmado_na_pagina": True}])
        self.assertEqual(r["avaliacao"]["efetividade"], 1.0)
        self.assertEqual(r["avaliacao"]["tipo"], "reconhecimento")
        self.assertIsNone(r["avaliacao"]["motivo_do_insucesso"])
        self.assertIn("credita", r["avaliacao"]["explicacao"])

    def test_nome_sem_prova_nao_conta(self):
        from src.aprendizados_piloto import avaliar
        r = avaliar(self._Mudo(), {"motor": "sindico-aberto", "tipo": "reconhecimento", "licao": "x"},
                    [{"titulo": "Empresa X", "trecho": "", "confirmado_na_pagina": False}])
        self.assertEqual(r["avaliacao"]["efetividade"], 0.0)
        self.assertEqual(r["avaliacao"]["motivo_do_insucesso"], "rastro_sem_prova")

    def test_pagina_sem_credito_registra_o_motivo(self):
        from src.aprendizados_piloto import avaliar
        r = avaliar(self._Mudo(), {"motor": "sindico-aberto", "tipo": "reconhecimento", "licao": "x"}, [])
        self.assertEqual(r["avaliacao"]["motivo_do_insucesso"], "sem_rastro")
        self.assertIn("não creditou ninguém", r["avaliacao"]["explicacao"])
