"""O vigia de prazos tem de enxergar os prazos que a verificacao ja confirmou.

O caso real, medido na inspecao de 10/09/2026: src.prazos lia apenas a base de
oportunidades coletadas — hoje quase toda formada por edicoes de diario oficial
com prazo_texto nulo — e devolvia:

    com_prazo: 0 | criticos: 0 | sem_prazo: 17.493

Zero prazos em dezessete mil registros, abrir_issue em falso desde 03/09 e o
passo "Abrir issue de prazos a vencer" do workflow nunca disparando. Ao mesmo
tempo, docs/dados/verificacao_467_2026-09-09.json tinha 339 prazos confirmados em
documento oficial e 55 editais abertos, e nenhum modulo o lia.

O vigia nao estava quebrado: estava olhando para a base errada.
"""
import json
import unittest
from datetime import date
from pathlib import Path

from src import prazos as P

ROOT = Path(__file__).resolve().parents[1]
HOJE = date(2026, 9, 12)


class TesteBasesVerificadas(unittest.TestCase):
    def test_as_bases_verificadas_estao_declaradas(self):
        nomes = [c.name for c in P.BASES_VERIFICADAS]
        self.assertIn("verificacao_467_2026-09-09.json", nomes)
        self.assertIn("nao_verificados.json", nomes)

    def test_le_prazo_confirmado_da_base_verificada(self):
        linhas = P._linhas_verificadas(HOJE, [30, 15, 7, 3, 1], set())
        self.assertTrue(linhas, "nenhum prazo veio das bases verificadas")
        futuros = [x for x in linhas if x["dias_restantes"] >= 0]
        self.assertTrue(futuros, "nenhum prazo em aberto veio das bases verificadas")

    def test_reprovado_por_objeto_nao_vai_ao_alarme(self):
        for linha in P._linhas_verificadas(HOJE, [30], set()):
            self.assertNotEqual(linha["status"], "reprovado", linha["id"])

    def test_nao_repete_o_mesmo_edital(self):
        linhas = P._linhas_verificadas(HOJE, [30], set())
        chaves = [(str(x["titulo"])[:120], x["vencimento"]) for x in linhas]
        self.assertEqual(len(chaves), len(set(chaves)),
                         "o mesmo edital entrou mais de uma vez no alarme")

    def test_observacao_declara_a_origem(self):
        for linha in P._linhas_verificadas(HOJE, [30], set()):
            self.assertIn("verificação individual", linha["observacao"])

    def test_id_ja_visto_nao_entra_de_novo(self):
        linhas = P._linhas_verificadas(HOJE, [30], set())
        alguns = {x["id"] for x in linhas}
        de_novo = P._linhas_verificadas(HOJE, [30], set(alguns))
        self.assertFalse({x["id"] for x in de_novo} & alguns)


class TesteRelatorioDePrazos(unittest.TestCase):
    """O relatorio gravado nao pode voltar a dizer zero."""

    def setUp(self):
        self.relatorio = json.loads((ROOT / "estado/prazos.json").read_text(encoding="utf-8"))

    def test_o_vigia_nao_esta_cego(self):
        self.assertGreater(self.relatorio["com_prazo"], 0,
                           "zero prazos: o vigia voltou a olhar so para a base errada")

    def test_ha_prazo_em_aberto_no_relatorio(self):
        futuros = [x for x in self.relatorio["itens"] if x["dias_restantes"] >= 0]
        self.assertTrue(futuros)

    def test_alerta_dispara_quando_ha_critico(self):
        alerta = json.loads((ROOT / "estado/alerta_prazos.json").read_text(encoding="utf-8"))
        criticos = self.relatorio["criticos"]
        self.assertEqual(alerta["abrir_issue"], criticos > 0)
        if criticos:
            self.assertIn("dia(s)", alerta["corpo"])


if __name__ == "__main__":
    unittest.main()
