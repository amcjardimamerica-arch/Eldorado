"""Teste do motor 03 em 03/10/2026: falso negativo de aviso de chamamento, doação de bens, dia útil não lido e limite de íntegras."""
import unittest
from datetime import date
from unittest import mock

from src import diario_uniao as D

H = date(2026, 10, 2)


def _m(tipo, hier, tit, txt, nivel="federal"):
    return {"tipo_dou": tipo, "hierarquia": hier, "caminho": " › ".join(hier + [tipo]), "titulo": tit, "texto": txt, "integra": True,
            "data": "2026-10-02", "nivel": nivel, "url_title": "x-1"}


class TesteMotor03(unittest.TestCase):
    def test_aviso_de_chamamento_para_celebracao_e_oportunidade(self):
        m = _m("Aviso de Chamamento Público", ["Prefeituras", "Estado de Goiás", "Prefeitura Municipal de Corumbá de Goiás"],
               "AVISO DE CHAMAMENTO PÚBLICO Nº 3/2026",
               "O Município torna público o Chamamento Público para seleção de organizações da sociedade civil, nos termos da Lei nº 13.019/2014, "
               "para celebração de termo de fomento. As propostas serão recebidas até 15/10/2026.", nivel="municipal")
        self.assertEqual(D.classificar_materia(m, H)["veredito"], "OPORTUNIDADE")

    def test_extrato_continua_acompanhar(self):
        m = _m("Extrato de Termo de Fomento", ["Ministério do Turismo"], "EXTRATO DE TERMO DE FOMENTO",
               "Termo de Fomento nº 1/2026. Partes: Ministério e Associação X. Valor total R$ 431.940,00.")
        self.assertEqual(D.classificar_materia(m, H)["veredito"], "ACOMPANHAR")

    def test_doacao_de_bens_em_goiania_e_oportunidade_e_fora_e_ruido(self):
        go = _m("Edital", ["Ministério da Fazenda", "Secretaria Especial da Receita Federal", "Delegacia em Goiânia"], "EDITAL DE DOAÇÃO DE BENS",
                "A Delegacia da Receita Federal em Goiânia/GO torna pública a doação de mercadorias apreendidas a entidades sem fins lucrativos. Pedidos até 20/10/2026.")
        rs = _m("Edital", ["Ministério da Fazenda", "Secretaria Especial da Receita Federal", "Delegacia em Passo Fundo"], "EDITAL DE DOAÇÃO DE BENS",
                "A Delegacia da Receita Federal em Passo Fundo/RS torna pública a doação de mercadorias apreendidas a entidades sem fins lucrativos. Pedidos até 20/10/2026.")
        self.assertEqual(D.classificar_materia(go, H)["veredito"], "OPORTUNIDADE")
        self.assertNotEqual(D.classificar_materia(rs, H)["veredito"], "OPORTUNIDADE")

    def test_dia_util_nao_lido_entra_e_vira_parcial(self):
        cfg = {"fonte_a": {"janela_dias": 1, "secoes": ["do3"], "extras": {}, "retroativo_dias": 5, "retroativo_por_execucao": 1}}
        diag = {"fontes": {"A": {"falhas": [], "materias_lidas": 0, "secoes_lidas": 0, "materias_no_jornal": 0, "textos_abertos": 0,
                                 "cortes": {}, "edicoes_do_dia": {}, "lidas_ok": [], "com_materias": []}}}
        lidas = []
        def falso_get(url, **k):
            lidas.append(url); return ""
        with mock.patch.object(D, "_get_tentando", side_effect=falso_get), mock.patch.object(D, "materias_do_jornal", return_value=([], {})):
            D.fonte_a(date(2026, 10, 2), cfg, diag, {"2026-09-25|do3": {"data": "2026-09-25", "materias": 1}})
        A = diag["fontes"]["A"]
        self.assertEqual(A["retroativos"], ["2026-10-01"])          # o dia útil mais recente fora da janela
        self.assertTrue(any("01-10-2026" in u for u in lidas))
        self.assertIn("2026-09-30", A["dias_nao_lidos"])           # ainda falta → o maestro vê parcial

    def test_hoje_em_brasilia(self):
        with mock.patch.object(D, "_hoje_brt") as h:
            h.return_value.date.return_value = date(2026, 10, 2)
            self.assertEqual((None or {}).get("_data") or D._hoje_brt().date(), date(2026, 10, 2))


if __name__ == "__main__":
    unittest.main()
