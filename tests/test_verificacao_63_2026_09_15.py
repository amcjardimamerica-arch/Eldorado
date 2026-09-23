"""A verificacao de 15/09/2026 tem de estar no sistema, e as correcoes tem de valer.

Os 63 editais que o relatorio listava como nao verificados foram conferidos um a
um na fonte oficial. Dois resultados desta rodada nao podem se perder:

  CONANDA/MDHC 01/2026 — a RETIFICACAO publicada ao lado do edital prorrogou o
  envio de propostas de 17/09 para 11/10/2026 e elevou a abrangencia exigida de
  tres para cinco regioes. O sistema tinha a data velha.

  Fundacao Maria Emilia — o dominio antigo tem certificado invalido e o dominio
  vivo e mariaemilia.org.br. O edital FME Transforma 02/2026 vai ate 30/10/2026.
  Essa pendencia estava aberta desde 09/09 como "precisa de telefone".
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/dados/verificacao_63_2026-09-15.json"


def base():
    return json.loads(BASE.read_text(encoding="utf-8"))


class TesteBaseDaVerificacao(unittest.TestCase):
    def test_a_base_existe_e_tem_os_63(self):
        d = base()
        self.assertEqual(d["total"], 63)
        self.assertEqual(len(d["itens"]), 63)

    def test_resumo_bate_com_a_lista(self):
        d = base()
        vere = {}
        for item in d["itens"].values():
            vere[item["veredito"]] = vere.get(item["veredito"], 0) + 1
        self.assertEqual(vere, d["resumo"]["veredito"])

    def test_todo_item_declara_a_rota_e_a_observacao(self):
        for chave, item in base()["itens"].items():
            self.assertTrue(item.get("observacao"), chave)
            self.assertTrue(item.get("rota_usada"), chave)

    def test_nenhuma_data_sem_observacao_que_a_explique(self):
        """Data nula so vale com o motivo escrito — e a regra do nulo honesto."""
        for chave, item in base()["itens"].items():
            if not item.get("fim"):
                self.assertGreater(len(item.get("observacao") or ""), 40, chave)


class TesteCorrecoesQueNaoPodemSePerder(unittest.TestCase):
    def test_conanda_foi_prorrogado_para_onze_de_outubro(self):
        item = base()["itens"]["97292f2d3c686703e79e"]
        self.assertEqual(item["fim"], "2026-10-11",
                         "a retificacao do MDHC prorrogou de 17/09 para 11/10/2026")
        self.assertIn("RETIFICACAO", item["observacao"].upper())
        self.assertIn("11/10/2026", item["observacao"])
        self.assertEqual(item["veredito"], "aprovado")

    def test_fundacao_maria_emilia_com_o_dominio_vivo(self):
        item = base()["itens"]["0c3d1eb59b2a598a0393"]
        self.assertEqual(item["fim"], "2026-10-30")
        self.assertIn("mariaemilia.org.br", item["pagina_oficial"])
        self.assertNotIn("fundacaomariaemilia.org.br", item["pagina_oficial"])

    def test_ipu_fecha_um_dia_antes_do_que_a_base_tinha(self):
        item = base()["itens"]["2ba35f9a49970753e57d"]
        self.assertEqual(item["fim"], "2026-09-23")
        self.assertEqual(item["fim_anterior"], "2026-09-24")
        self.assertTrue(item["mudou_prazo"])

    def test_jaru_sao_dois_editais_diferentes(self):
        itens = base()["itens"]
        self.assertNotEqual(itens["8c6a2a0e25ff8b32702d"]["fim"],
                            itens["ccf2796183121fdbd963"]["fim"],
                            "196 e 197 sao chamamentos distintos, com prazos distintos")


class TesteLigacaoComAsRotinas(unittest.TestCase):
    """A base nova nao pode virar arquivo orfao, como aconteceu com a de 09/09."""

    def test_o_vigia_de_prazos_le_esta_base(self):
        from src import prazos
        nomes = [c.name for c in prazos.BASES_VERIFICADAS]
        self.assertIn("verificacao_63_2026-09-15.json", nomes)
        # A regra e "a mais recente vence", nao "a de 15/09 vence". Fixar o nome
        # da base de 15/09 aqui fez este teste quebrar em 23/09, quando o
        # fechamento novo — que corrige a chave de Osorio/RS — assumiu a frente.
        # O que se cobra e a ORDEM: da mais nova para a mais velha.
        datas = [re.search(r"(\d{4}-\d{2}-\d{2})", n) for n in nomes]
        datadas = [m.group(1) for m in datas if m]
        self.assertEqual(datadas, sorted(datadas, reverse=True),
                         f"bases fora de ordem de recencia: {nomes}")
        self.assertGreaterEqual(datadas[0], "2026-09-15",
                                "a verificacao mais recente tem de vencer as anteriores")

    def test_a_fila_de_pesquisa_le_esta_base(self):
        from src import abertos_sem_informacao
        nomes = [c.name for c in abertos_sem_informacao.BASES_VERIFICADAS]
        self.assertIn("verificacao_63_2026-09-15.json", nomes)

    def test_o_prazo_do_conanda_chega_ao_alarme(self):
        from datetime import date
        from src import prazos
        linhas = prazos._linhas_verificadas(date(2026, 9, 15), [30, 15, 7, 3, 1], set())
        # a chave pode vir completa (20 caracteres) ou truncada em 8, conforme a
        # base de origem: o vigia usa a chave como ela esta em cada arquivo
        conanda = [x for x in linhas if str(x["id"]).startswith("97292f2d")]
        self.assertTrue(conanda, "o CONANDA nao chegou ao vigia de prazos")
        self.assertEqual(conanda[0]["vencimento"], "2026-10-11")


class TesteCuradoriaDaRodada(unittest.TestCase):
    def test_as_duas_fontes_novas_entraram(self):
        from src import curadoria_fontes
        programas = {f.get("programa") for f in curadoria_fontes.carregar()["fontes_novas"]}
        self.assertIn("MDHC / CONANDA — Chamamentos publicos de fomento a OSC", programas)
        self.assertIn("Fundacao Maria Emilia — Edital FME Transforma", programas)

    def test_a_armadilha_do_amparo_legal_esta_registrada(self):
        from src import curadoria_fontes
        urls = " ".join(a.get("url", "") for a in curadoria_fontes.carregar()["armadilhas"])
        self.assertIn("amparoLegal", urls)

    def test_o_dominio_morto_da_maria_emilia_e_armadilha(self):
        from src import curadoria_fontes
        arm = [a for a in curadoria_fontes.carregar()["armadilhas"]
               if "fundacaomariaemilia" in a.get("url", "")]
        self.assertEqual(len(arm), 1, "o dominio morto tem de ter UMA armadilha, nao duas")
        self.assertIn("mariaemilia.org.br", arm[0]["motivo"],
                      "a armadilha tem de dizer qual e o dominio vivo")


if __name__ == "__main__":
    unittest.main()
