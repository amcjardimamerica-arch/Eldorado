"""Incentivos fiscais das empresas — o que a fonte oficial permite afirmar, e só isso.

O caso real (26/09/2026): o campo `destinacoes_5_anos` estava vazio em todas as
empresas da Biblioteca de Alexandria, os 26 caches do SALIC gravavam "falha:
HTTPError" porque a API do MinC mudou de endereço, e o painel exibia como
etiqueta os mecanismos que cada empresa "usa" — hipóteses de conhecimento
público, apresentadas como fato. Quatro CNPJs do ranking eram de outra empresa
(a "Vale" era uma fábrica de fertilizantes; a "Stone", a Bridgestone), e dois
registros nem eram empresa: um fragmento de data e um trecho de notícia.

Estes testes cobram que nada disso volte.
"""
import json
import re
import unittest
from pathlib import Path

from src import incentivos_empresas as I

ROOT = Path(__file__).resolve().parents[1]


class TesteFontesGravadas(unittest.TestCase):
    """Os três extratos oficiais existem e declaram de onde vieram."""

    def test_os_tres_extratos_existem(self):
        for caminho in (I.ROUANET, I.GOYAZES, I.PAT):
            self.assertTrue(caminho.exists(), caminho)

    def test_extrato_rouanet_declara_a_fonte_do_minc(self):
        d = json.loads(I.ROUANET.read_text(encoding="utf-8"))
        self.assertIn("api.salic.cultura.gov.br/api/v1/incentivadores", d["fonte"]["total_por_cnpj"])
        self.assertIn("aplicacoes.cultura.gov.br/comparar", d["fonte"]["doacoes_por_cnpj"])
        self.assertGreaterEqual(len(d["empresas"]), 95)

    def test_toda_doacao_rouanet_tem_data_iso_e_valor_positivo(self):
        d = json.loads(I.ROUANET.read_text(encoding="utf-8"))
        iso = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for cnpj, reg in d["empresas"].items():
            for data, _pronac, valor, _p, _proj in reg["doacoes"]:
                self.assertTrue(iso.match(data or ""), f"{cnpj}: data {data!r}")
                self.assertGreater(valor, 0, cnpj)

    def test_goyazes_bate_com_os_totais_publicados_pela_secult(self):
        """A soma lida das planilhas é a mesma que a Secult publica no rodapé."""
        d = json.loads(I.GOYAZES.read_text(encoding="utf-8"))
        for ano, total in d["totais_publicados"].items():
            soma = round(sum(l["valor"] or 0 for l in d["linhas"] if str(l["ano"]) == ano), 2)
            self.assertAlmostEqual(soma, total, places=2, msg=ano)

    def test_pat_registra_o_arquivo_e_o_hash(self):
        d = json.loads(I.PAT.read_text(encoding="utf-8"))
        self.assertEqual(len(d["sha256"]), 64)
        self.assertIn("31/03/2026", d["fonte"])
        self.assertIn("não prova Lucro Real", d["nota"])


class TesteRouanet(unittest.TestCase):

    def test_empresa_que_destinou_tem_total_e_doacoes(self):
        r = I.rouanet_de("01838723000127")  # BRF
        self.assertEqual(r["status"], "destinou")
        self.assertGreater(r["total_historico_api"], 0)
        self.assertGreater(r["doacoes_registradas"], 0)
        self.assertTrue(r["ultimos_5_anos"]["anos"])

    def test_empresa_que_o_salic_nao_conhece_sai_como_nao_consta(self):
        r = I.rouanet_de("01257995000133")  # Goiasminas: 404 na API, nenhuma doação
        self.assertEqual(r["status"], "nao_consta")
        self.assertNotIn("total_historico_api", r)

    def test_cnpj_fora_do_lote_nao_vira_zero(self):
        """Não lido é diferente de não destinou."""
        r = I.rouanet_de("11111111000111")
        self.assertEqual(r["status"], "nao_lido")

    def test_janela_de_cinco_anos_so_conta_doacao_desde_o_corte(self):
        r = I.rouanet_de("02558157000162")  # Telefônica: doa desde 2000
        corte = I._corte()
        for d in r["doacoes_5_anos"]:
            self.assertGreaterEqual(int(d["data"][:4]), corte)
        self.assertLess(r["ultimos_5_anos"]["valor"], r["total_historico_doacoes"])

    def test_doacao_antiga_nao_confirma_lucro_real_de_hoje(self):
        r = I.rouanet_de("60498706000157")  # Cargill: última doação fora da janela
        self.assertEqual(r["status"], "destinou")
        self.assertFalse(r["ultimos_5_anos"]["anos"])
        self.assertIsNone(I.lucro_real_pela_rouanet(r))

    def test_doacao_recente_confirma_lucro_real_com_a_lei(self):
        lucro = I.lucro_real_pela_rouanet(I.rouanet_de("01838723000127"))
        self.assertEqual(lucro["classe"], "confirmado")
        self.assertIn("8.313", lucro["motivo"])

    def test_divergencia_entre_as_bases_do_minc_fica_registrada(self):
        r = I.rouanet_de("33041260000164")  # Casas Bahia: API e relatório divergem
        self.assertIn("divergencia", r)
        self.assertIsNotNone(r["total_historico_api"])
        self.assertIsNotNone(r["total_historico_doacoes"])


class TesteGoyazes(unittest.TestCase):

    def test_as_tres_grafias_da_bela_vista_sao_a_mesma_empresa(self):
        g = I.goyazes_de("02089969000106", ["LATICINIOS BELA VISTA LTDA"])
        self.assertEqual(g["status"], "destinou")
        self.assertEqual(set(g["por_ano"]), {"2024", "2025", "2026"})
        self.assertGreaterEqual(len(g["grafias_na_planilha"]), 3)

    def test_valor_do_goyazes_e_do_projeto_nao_da_cota(self):
        g = I.goyazes_de("01543032000104", ["EQUATORIAL GOIAS DISTRIBUIDORA DE ENERGIA S/A"])
        self.assertIn("não é a cota individual", g["nota"])
        for p in g["projetos"]:
            self.assertIn("empresas_no_projeto", p)

    def test_empresa_ausente_das_planilhas(self):
        g = I.goyazes_de("33000167000101", ["PETROLEO BRASILEIRO S A PETROBRAS"])
        self.assertEqual(g["status"], "nao_consta_2024_2026")

    def test_laticinios_fleury_nao_e_o_laboratorio_fleury(self):
        """Nome parecido não é a mesma empresa."""
        g = I.goyazes_de("60840055000131", ["Fleury", "Fleury S/A", "FLEURY SA"])
        self.assertEqual(g["status"], "nao_consta_2024_2026")

    def test_descobertas_do_goyazes_ficam_sem_cnpj_e_com_proximo_passo(self):
        novas = I.descobertas_goyazes(set())
        self.assertGreater(len(novas), 50)
        for n in novas:
            self.assertIsNone(n["cnpj"])
            self.assertIn("CNPJ", n["proximo_passo"])


class TestePAT(unittest.TestCase):

    def test_inscricao_no_pat_nunca_confirma_lucro_real(self):
        f = I.ficha("GOIASMINAS INDUSTRIA DE LATICINIOS LTDA", "01257995000133")
        self.assertEqual(f["mecanismos"]["PAT"]["status"], "inscrita")
        self.assertNotIn("lucro_real", f)  # não destinou pela Rouanet: nada confirma o regime
        self.assertIn("não prova", f["mecanismos"]["PAT"]["leitura"])

    def test_inscricao_so_inativa(self):
        self.assertEqual(I.pat_de("73410326000160")["status"], "inscricao_inativa")  # Cervejaria Petrópolis


class TesteMecanismosSemFonte(unittest.TestCase):
    """LIE, FIA, Idoso, PRONON e PRONAS: nulo com motivo, nunca estimativa."""

    def test_todos_saem_nulos_com_motivo(self):
        f = I.ficha("BRF", "01.838.723/0001-27")
        for m in ("LIE", "FIA", "Fundo do Idoso", "PRONON", "PRONAS/PCD"):
            self.assertIsNone(f["mecanismos"][m]["valor"], m)
            self.assertTrue(f["mecanismos"][m]["motivo"], m)
            self.assertNotEqual(f["mecanismos"][m]["status"], "destinou", m)

    def test_lie_diz_quando_consultar_de_novo(self):
        f = I.ficha("BRF", "01838723000127")
        self.assertEqual(f["mecanismos"]["LIE"]["status"], "bloqueado_defeso_eleitoral")
        self.assertEqual(f["mecanismos"]["LIE"]["retomar_em"], "2026-10-26")

    def test_fia_e_idoso_apontam_o_caminho_da_lei_de_acesso(self):
        f = I.ficha("BRF", "01838723000127")
        self.assertIn("12.527", f["mecanismos"]["FIA"]["caminho"])
        self.assertIn("acesso à informação", f["mecanismos"]["Fundo do Idoso"]["caminho"])


class TesteCnpj(unittest.TestCase):

    def test_os_quatro_cnpjs_errados_sao_corrigidos(self):
        for nome, c in I.CORRECOES_CNPJ.items():
            f = I.ficha(nome, c["errado"])
            self.assertEqual(f["cnpj"], c["correto"], nome)
            self.assertIn("prova", f["cnpj_corrigido"])

    def test_a_correcao_nao_atinge_a_empresa_verdadeira_dona_do_cnpj(self):
        """O CNPJ 08334818000152 é da Nestlé Nordeste; só o registro 'Nestlé' muda."""
        f = I.ficha("NESTLE NORDESTE ALIMENTOS E BEBIDAS LTDA", "08334818000152")
        self.assertEqual(f["cnpj"], "08334818000152")

    def test_nome_so_ganha_cnpj_com_prova_do_orgao(self):
        for nome, (cnpj, prova) in I.RESOLUCAO_POR_NOME.items():
            self.assertEqual(len(cnpj), 14, nome)
            self.assertRegex(prova, r"SALIC|PAT|Goyazes|mesma pessoa jurídica", nome)

    def test_marca_de_grupo_fica_sem_cnpj(self):
        f = I.ficha("Sicoob", None)
        self.assertIsNone(f["cnpj"])
        self.assertEqual(f["mecanismos"]["Rouanet"]["status"], "sem_cnpj")

    def test_entidade_isenta_nao_recebe_potencial_fiscal(self):
        f = I.ficha("Sebrae Goiás", None)
        self.assertFalse(f["incentivo_fiscal"]["aplica"])


class TesteRegistrosFalsos(unittest.TestCase):

    def test_fragmento_de_data_e_trecho_de_noticia_sao_descartados(self):
        for nome in ("de janeiro de 2026", "WhatsApp Agenda Grupo", "Diário de Goiás Comunicação LTDA"):
            self.assertTrue(I.ficha(nome, None).get("descartar"), nome)

    def test_filtro_do_ranking_barra_nome_que_nao_e_nome(self):
        from src.biblioteca_empresas import parece_nome_de_empresa
        self.assertFalse(parece_nome_de_empresa("de janeiro de 2026"))
        self.assertFalse(parece_nome_de_empresa("12 de março"))
        self.assertTrue(parece_nome_de_empresa("CIPLAN CIMENTO PLANALTO SA"))
        self.assertTrue(parece_nome_de_empresa("Grupo Mateus"))


class TesteAplicacaoNoRanking(unittest.TestCase):

    def setUp(self):
        self.bases = I.carregar_bases()
        self.itens = [
            {"nome": "Vale", "cnpj": "53400818000168", "pontos": 60, "incentivos": ["Rouanet", "LIE", "FIA"],
             "por": ["40: 5º maior contribuinte", "9: usa 3 mecanismo(s) de incentivo (Rouanet, LIE, FIA)"]},
            {"nome": "Telefônica Vivo", "cnpj": None, "pontos": 50, "incentivos": ["Rouanet"], "por": ["3: usa 1 mecanismo(s) de incentivo (Rouanet)"]},
            {"nome": "TELEFONICA BRASIL S.A.", "cnpj": "02.558.157/0001-62", "pontos": 40, "incentivos": None, "por": []},
            {"nome": "de janeiro de 2026", "cnpj": None, "pontos": 28, "por": []},
        ]

    def test_hipotese_sai_da_etiqueta_e_fica_guardada(self):
        saida = I.aplicar_em_ranking(self.itens, "destinacao_tributaria", self.bases)
        vale = next(x for x in saida if x["nome"] == "Vale")
        self.assertEqual(vale["incentivos_hipotese"], ["Rouanet", "LIE", "FIA"])
        self.assertNotIn("LIE", vale["incentivos"] or [])
        self.assertNotIn("FIA", vale["incentivos"] or [])
        self.assertFalse(any("usa 3 mecanismo" in l for l in vale["por"]))

    def test_cnpj_corrigido_no_ranking(self):
        saida = I.aplicar_em_ranking(self.itens, "destinacao_tributaria", self.bases)
        vale = next(x for x in saida if x["nome"] == "Vale")
        self.assertEqual(I.so_digitos(vale["cnpj"]), "33592510000154")

    def test_mesma_pessoa_juridica_aparece_uma_vez(self):
        saida = I.aplicar_em_ranking(self.itens, "destinacao_tributaria", self.bases)
        tel = [x for x in saida if I.so_digitos(x.get("cnpj")) == "02558157000162"]
        self.assertEqual(len(tel), 1)
        self.assertTrue(tel[0].get("tambem_listada_como"))

    def test_registro_falso_sai_do_ranking(self):
        saida = I.aplicar_em_ranking(self.itens, "destinacao_tributaria", self.bases)
        self.assertFalse(any(x["nome"] == "de janeiro de 2026" for x in saida))

    def test_aplicar_duas_vezes_da_o_mesmo_resultado(self):
        uma = I.aplicar_em_ranking(self.itens, "destinacao_tributaria", self.bases)
        duas = I.aplicar_em_ranking(uma, "destinacao_tributaria", self.bases)
        self.assertEqual([(x["nome"], x["pontos"]) for x in uma], [(x["nome"], x["pontos"]) for x in duas])

    def test_etiqueta_so_mostra_o_que_esta_na_janela(self):
        itens = [{"nome": "Cargill", "cnpj": "60.498.706/0001-57", "pontos": 50, "incentivos": ["FIA", "Rouanet"], "por": []}]
        cargill = I.aplicar_em_ranking(itens, "destinacao_tributaria", self.bases)[0]
        self.assertIsNone(cargill["incentivos"])  # última doação à Rouanet antes do corte
        self.assertEqual(cargill["incentivos_historico"], ["Rouanet"])


class TesteSaidasGravadas(unittest.TestCase):
    """O que foi gravado na biblioteca obedece às mesmas regras."""

    def test_base_verificada_existe_e_explica_os_mecanismos(self):
        d = json.loads(I.SAIDA.read_text(encoding="utf-8"))
        self.assertEqual(set(d["mecanismos"]), {"Rouanet", "Goyazes", "PAT", "LIE", "FIA", "Fundo do Idoso", "PRONON", "PRONAS/PCD"})
        self.assertGreater(d["resumo"]["rouanet"]["destinou"], 50)

    def test_nenhum_valor_fora_de_rouanet_e_goyazes(self):
        d = json.loads(I.SAIDA.read_text(encoding="utf-8"))
        for f in d["empresas"]:
            for m in ("LIE", "FIA", "Fundo do Idoso", "PRONON", "PRONAS/PCD"):
                self.assertIsNone(f["mecanismos"][m]["valor"], (f["nome"], m))

    def test_painel_de_goias_tem_destinacoes_e_nenhum_registro_falso(self):
        g = json.loads((ROOT / "biblioteca_alexandria/empresas/go/go.json").read_text(encoding="utf-8"))
        nomes = {e["nome"] for e in g["empresas"]}
        self.assertNotIn("WhatsApp Agenda Grupo", nomes)
        self.assertNotIn("Diário de Goiás Comunicação LTDA", nomes)
        com = [e for e in g["empresas"] if e["destinacoes_5_anos"]]
        self.assertGreater(len(com), 20)
        for e in com:
            for h in e["destinacoes_5_anos"]:
                self.assertIn(h["fonte"], ("SALIC/MinC", "Secult-GO"))

    def test_ranking_gravado_sem_hipotese_na_etiqueta(self):
        for cat in ("destinacao_tributaria", "patrocinio_privado"):
            d = json.loads((ROOT / f"biblioteca_alexandria/empresas/ranking_{cat}.json").read_text(encoding="utf-8"))
            for e in d["empresas"]:
                for m in e.get("incentivos") or []:
                    self.assertIn(m, ("Rouanet", "Goyazes"), (cat, e["nome"]))


class TesteMotorDeEmpresas(unittest.TestCase):

    def test_endereco_novo_da_api_do_salic(self):
        c = json.loads((ROOT / "config/empresas.json").read_text(encoding="utf-8"))
        self.assertIn("/api/v1/incentivadores", c["destinacoes"]["rouanet_salic"]["api"])

    def test_destinacoes_rouanet_le_a_base_verificada(self):
        from src.empresas import destinacoes_rouanet
        r = destinacoes_rouanet("01.838.723/0001-27")
        self.assertEqual(r["status"], "com_registro")
        self.assertTrue(all(i["fonte"] == "SALIC/MinC" for i in r["itens"]))


if __name__ == "__main__":
    unittest.main()
