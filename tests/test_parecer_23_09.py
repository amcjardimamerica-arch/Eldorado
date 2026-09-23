"""Atualização do parecer de oportunidades e as oito correções de motor (23/09)."""
import json, pathlib, unittest
from datetime import date
from src.correcoes_motor_23_09 import (ABRANGENCIA, alcance, territorio_do_objeto, elegivel,
                                       requisitos_de_habilitacao, papel_possivel, desdobrar,
                                       e_permanente, classificar_prazo, hora_de_encerramento,
                                       restricao_eleitoral, avaliar)
ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALISES = json.loads((ROOT / "dados/editais/analises.json").read_text(encoding="utf-8"))


class TesteAtualizacaoAplicada(unittest.TestCase):
    def test_o_registro_da_aplicacao_existe(self):
        r = json.loads((ROOT / "estado/parecer_23_09_aplicado.json").read_text(encoding="utf-8"))
        self.assertEqual(r["atualizados"], 19)
        self.assertEqual(r["excluidos"], 409)
        self.assertEqual(r["rebaixados"], 238)
        self.assertEqual(r["nao_encontrados_total"], 0)      # 655 de 655

    def test_excluido_e_marcado_nao_apagado(self):
        fora = [v for v in ANALISES.values() if isinstance(v, dict) and v.get("fora_do_objeto")]
        self.assertEqual(len(fora), 409)
        for v in fora[:20]:
            self.assertFalse(v["ativo"])
            self.assertTrue(v["excluido_porque"])             # o motivo fica escrito
            self.assertIn("não apagado", v["reversivel"])

    def test_rebaixado_diz_quando_volta(self):
        reb = [v for v in ANALISES.values() if isinstance(v, dict)
               and v.get("alcance") == "fora_de_abrangencia"]
        self.assertEqual(len(reb), 238)
        for v in reb[:20]:
            self.assertTrue(v["uf_do_edital"])
            self.assertIn("abrangência aprovada", v["volta_se"])

    def test_atualizado_guarda_a_data_da_confirmacao(self):
        at = [v for v in ANALISES.values() if isinstance(v, dict) and v.get("reverificado_em")]
        self.assertGreaterEqual(len(at), 19)
        for v in at[:10]:
            self.assertIn("parecer de oportunidades 23/09", v["reverificado_por"])

    def test_o_acervo_ativo_encolheu_para_o_que_serve(self):
        ativos = [v for v in ANALISES.values() if isinstance(v, dict) and v.get("ativo") is not False]
        self.assertLess(len(ativos), 200)                     # de 812 para ~165
        self.assertGreater(len(ativos), 50)


class TesteM1_AbrangenciaAntes(unittest.TestCase):
    def test_outra_uf_nao_entra_na_fila_de_verificacao(self):
        self.assertEqual(alcance({"uf": "RO", "titulo": "Chamamento de Jaru"})[0], "fora")
        self.assertFalse(avaliar({"uf": "SP", "titulo": "Edital municipal"})["verificar"])

    def test_goias_e_goiania_entram(self):
        self.assertEqual(alcance({"uf": "GO", "titulo": "Secult"})[0], "dentro")
        self.assertEqual(alcance({"titulo": "Edital da Prefeitura de Goiânia"})[0], "dentro")
        self.assertTrue(avaliar({"uf": "GO", "titulo": "x"})["verificar"])

    def test_nacional_entra(self):
        self.assertEqual(alcance({"titulo": "Edital de âmbito nacional"})[0], "dentro")

    def test_a_abrangencia_e_a_aprovada_pelo_titular(self):
        self.assertTrue(ABRANGENCIA["nacional"])
        self.assertEqual(ABRANGENCIA["estados"], ["GO"])
        self.assertEqual(ABRANGENCIA["municipios"], ["GO/Goiania"])

    def test_reproduz_o_veredito_do_parecer(self):
        """O filtro, sozinho, chega aos mesmos 238 que o parecer rebaixou."""
        fora = 0
        for k, v in ANALISES.items():
            if not isinstance(v, dict) or v.get("alcance") != "fora_de_abrangencia":
                continue
            e = dict(v)
            e["uf"] = v.get("uf_do_edital")
            if alcance(e)[0] == "fora":
                fora += 1
        self.assertEqual(fora, 238)


class TesteM2_NacionalTerritorial(unittest.TestCase):
    def test_funbio_no_litoral_do_parana_nao_e_nosso(self):
        e = {"titulo": "Chamada 07/2026", "objeto": "projetos no litoral do Paraná",
             "fonte_nome": "Funbio nacional"}
        self.assertTrue(territorio_do_objeto(e)[0])
        self.assertEqual(alcance(e)[0], "fora")
        self.assertIn("litoral do parana", alcance(e)[1])

    def test_fonte_nacional_sem_territorio_continua_valendo(self):
        self.assertFalse(territorio_do_objeto({"titulo": "Edital nacional", "objeto": "todo o país"})[0])


class TesteM3_RequisitoDeHabilitacao(unittest.TestCase):
    def test_o_fme_e_inelegivel_pelo_doutorado(self):
        """Em 09 e 15/09 o sistema chamou isto de 'a maior oportunidade aberta'."""
        ok, barreiras = elegivel({"objeto": "o coordenador deve possuir diploma de doutorado"})
        self.assertFalse(ok)
        self.assertIn("doutorado", barreiras[0])

    def test_conanda_tem_duas_barreiras(self):
        ok, b = elegivel({"objeto": "exige registro no CMDCA e execução em cinco regiões do país"})
        self.assertFalse(ok)
        self.assertGreaterEqual(len(b), 2)

    def test_requisito_que_a_associacao_tem_nao_e_barreira(self):
        r = requisitos_de_habilitacao("entidade com 2 anos de existência")
        self.assertTrue(r); self.assertFalse(r[0]["eliminatorio"])

    def test_edital_sem_requisito_especial_passa(self):
        self.assertTrue(elegivel({"objeto": "seleção de projetos culturais"})[0])


class TesteM4_PorteDoProponente(unittest.TestCase):
    def test_bndes_entra_como_organizacao_de_base(self):
        p = papel_possivel({"objeto": "projeto mínimo de R$ 20 milhões"})
        self.assertEqual(p["papel"], "organizacao_de_base")
        self.assertIn("organização de base", p["acao"])

    def test_projeto_na_faixa_permite_ser_proponente(self):
        self.assertEqual(papel_possivel({"objeto": "até R$ 500.000"})["papel"], "proponente")


class TesteM5_UmRegistroVariosEditais(unittest.TestCase):
    def test_porto_feliz_vira_cinco(self):
        e = {"id": "pf", "titulo": "Porto Feliz PNAB",
             "anexos": [{"nome": f"Edital 0{i}/2026 PNAB"} for i in range(1, 6)] + [{"nome": "anexo.pdf"}]}
        d = desdobrar(e)
        self.assertEqual(len(d), 5)
        self.assertEqual(len({x["numero_do_edital"] for x in d}), 5)
        self.assertTrue(all(x["desdobrado_de"] == "pf" for x in d))

    def test_registro_com_um_edital_nao_desdobra(self):
        self.assertEqual(len(desdobrar({"id": "x", "anexos": [{"nome": "Edital 01/2026"}]})), 1)


class TesteM6_MecanismoPermanente(unittest.TestCase):
    def test_receita_e_penas_saem_da_fila_de_prazo(self):
        for t in ("doação da Receita Federal", "prestação pecuniária da vara",
                  "Instituto Impactarte fluxo contínuo", "emenda parlamentar"):
            p = classificar_prazo({"titulo": t})
            self.assertEqual(p["classe"], "mecanismo_permanente", t)
            self.assertTrue(p["sai_da_fila_de_prazo"])
            self.assertIsNone(p["prazo"])

    def test_edital_normal_continua_com_prazo(self):
        p = classificar_prazo({"titulo": "Edital de fomento", "fim": "2026-10-30"})
        self.assertEqual(p["classe"], "edital_com_prazo")
        self.assertFalse(p["sai_da_fila_de_prazo"])


class TesteM7_Hora(unittest.TestCase):
    def test_le_a_hora_quando_o_edital_declara(self):
        self.assertEqual(hora_de_encerramento("inscrições até as 17h00"), "17:00")
        self.assertEqual(hora_de_encerramento("até 23h59 do dia 30"), "23:59")
        self.assertEqual(hora_de_encerramento("até as 9h"), "09:00")
        self.assertIsNone(hora_de_encerramento("até o dia 30 de outubro"))


class TesteM8_RestricaoEleitoral(unittest.TestCase):
    def test_receita_federal_em_ano_eleitoral(self):
        r = restricao_eleitoral({"titulo": "Doação de mercadoria apreendida Receita Federal"},
                                hoje=date(2026, 9, 23))
        self.assertTrue(r["em_vigor"])
        self.assertIn("habilitar agora", r["recomendacao"])
        self.assertIn("habilitação", r["o_que_continua"])      # o que para é a entrega

    def test_fora_de_ano_eleitoral_nao_restringe(self):
        r = restricao_eleitoral({"titulo": "Receita Federal mercadoria apreendida"},
                                hoje=date(2027, 3, 1))
        self.assertFalse(r["em_vigor"])

    def test_edital_comum_nao_tem_restricao(self):
        self.assertIsNone(restricao_eleitoral({"titulo": "Edital de cultura"}))
