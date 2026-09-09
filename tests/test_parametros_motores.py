"""Testes de aceite dos parâmetros da auditoria de 09/09/2026.

Cada teste corresponde ao teste_de_aceite declarado no parâmetro. A regra de ouro
(P24) é a primeira: falso positivo é o erro caro.
"""
import json
import pathlib
import unittest

from src.parametros_motores import (avaliar_medido, enquadramento_legal, prazo_confiavel,
                                    sinalizadores_de_anexos, fontes_atrasadas, zona_de_atencao,
                                    auditoria_cega, META_ZONA_ATENCAO, CADENCIA_DIAS)
from src.inconformidade import avaliar

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteParametrosDaAuditoria(unittest.TestCase):
    def test_p24_aprovados_nunca_sao_barrados(self):
        """P24: nenhuma regra nova pode reprovar um objeto de fomento legítimo."""
        for t in ("Chamamento público para seleção de OSC para termo de fomento em cultura",
                  "Edital de fomento a projetos culturais de organizações da sociedade civil sem fins lucrativos",
                  "Termo de colaboração com organização da sociedade civil para acolhimento institucional",
                  "Seleção pública de projetos culturais — Lei 13.019/2014"):
            self.assertTrue(avaliar(t)["ok"], t)
            self.assertNotEqual(avaliar_medido(t).get("veredito"), "reprovado", t)

    def test_p04_amparo_legal_decide_antes_do_texto(self):
        """P04: objeto idêntico aprova sob a 13.019 e reprova sob a 14.133."""
        objeto = "Credenciamento de pessoas jurídicas para prestação de serviços de acolhimento"
        self.assertEqual(enquadramento_legal(objeto, "Lei 13.019/2014")["presuncao"], "parceria")
        self.assertEqual(enquadramento_legal(objeto, "Lei 14.133/2021")["presuncao"], "contratação")
        self.assertIsNone(avaliar_medido(objeto, "Lei 13.019/2014").get("veredito"))
        self.assertEqual(avaliar_medido(objeto, "Lei 14.133/2021").get("veredito"), "reprovado")

    def test_p05_credenciamento_sob_14133_presume_contratacao(self):
        leg = enquadramento_legal("credenciamento de empresas", "Lei 14.133/2021")
        self.assertIn("art. 6º, XLIII", leg["fundamento"])
        self.assertTrue(leg["decide"])
        resgate = enquadramento_legal("termo de fomento com organizações da sociedade civil sem fins lucrativos", "Lei 14.133/2021")
        self.assertTrue(resgate["resgatado"])          # instrumento nomeado + destinatário exclusivo resgata

    def test_p06_a_p09_regras_com_acerto_medido(self):
        self.assertEqual(avaliar_medido("CREDENCIAMENTO DE ENTIDADES, com ou sem fins lucrativos, para prestação de serviço")["veredito"], "reprovado")
        self.assertEqual(avaliar_medido("Credenciamento de pessoas jurídicas para realização de exames")["veredito"], "reprovado")
        self.assertEqual(avaliar_medido("Seleção de prestadoras de serviço médico ao município")["veredito"], "reprovado")
        # P09: a exceção resgata
        self.assertIsNone(avaliar_medido("Credenciamento de pessoas jurídicas de direito privado, sem fins lucrativos, para acolhimento").get("veredito"))

    def test_p29_objeto_curto_nao_reprova(self):
        r = avaliar_medido("Chamamento público 01/2026")
        self.assertEqual(r["veredito"], "atencao"); self.assertTrue(r["prioridade_de_leitura"])

    def test_p11_p12_p30_o_que_nao_e_prazo_de_inscricao(self):
        self.assertFalse(prazo_confiavel("2026-05-04", "2026-05-04")["confiavel"])          # P11
        self.assertEqual(prazo_confiavel("2026-05-04", "2026-05-04")["parametro"], "P11")
        self.assertFalse(prazo_confiavel("2024-01-01", "2099-11-09")["confiavel"])          # P12
        self.assertFalse(prazo_confiavel(None, "2026-10-01", "prazo de vigência do credenciamento")["confiavel"])  # P30
        self.assertTrue(prazo_confiavel("2026-09-01", "2026-10-30")["confiavel"])

    def test_p14_revogacao_e_errata(self):
        rev = sinalizadores_de_anexos([{"nome": "Termo de revogação do edital 01/2026"}])
        self.assertTrue(rev["revogado"]); self.assertIn("encerrar", rev["acao"])
        err = sinalizadores_de_anexos([{"nome": "Errata 2 — prorrogação do prazo"}])
        self.assertTrue(err["tem_errata"]); self.assertIn("reler o prazo", err["acao"])

    def test_p21_cadencia_de_sete_dias(self):
        self.assertEqual(CADENCIA_DIAS, 7)
        c = fontes_atrasadas()
        self.assertIn("art. 26", c["fundamento"]); self.assertIn("30 dias", c["fundamento"])
        self.assertIsInstance(c["atrasadas"], int)

    def test_p25_zona_de_atencao_tem_meta(self):
        z = zona_de_atencao()
        self.assertEqual(z["meta"], META_ZONA_ATENCAO); self.assertEqual(META_ZONA_ATENCAO, 0.15)
        self.assertIn("proporcao", z); self.assertIn("custo", z)

    def test_p31_auditoria_cega_de_recall(self):
        a = auditoria_cega(5, 2)
        self.assertGreaterEqual(a["sorteados"], 5)
        self.assertIn("NUNCA entrou", a["regra"])
        arq = json.loads((ROOT / "estado/auditoria_cega.json").read_text(encoding="utf-8"))
        self.assertTrue(all(x.get("conferir") for x in arq["itens"][:5]))

    def test_bloqueio_e_da_ultima_leitura_nao_do_historico(self):
        """09/09: motores apareciam como 'bloqueado' por causa do histórico acumulado do
        domínio. A ABCR, com 23 editais encontrados e resposta 200, aparecia bloqueada
        por 2 recusas antigas. Agora o rótulo vem da ÚLTIMA leitura."""
        from src.motores import _bloqueio_vigente
        reg = {"bloqueios": 60, "ultimo": "2026-09-09T00:00:00+00:00", "erros": {"HTTPError": 60}}
        respondeu = {"ultima": "2026-09-09T03:00:00+00:00", "saude": [{"http": 200}], "achados_total": 0}
        self.assertIsNone(_bloqueio_vigente(reg, respondeu))                      # respondeu agora
        entregando = {"ultima": "2026-09-09T03:00:00+00:00", "saude": [], "achados_total": 23}
        self.assertIsNone(_bloqueio_vigente(reg, entregando))                     # está achando editais
        falhou = {"ultima": "2026-09-09T03:00:00+00:00", "saude": [{"erro": "HTTPError", "code": 403}], "achados_total": 0}
        v = _bloqueio_vigente(reg, falhou)
        self.assertTrue(v and v["vigente"]); self.assertIn("falharam na última leitura", v["base"])
        self.assertIsNone(_bloqueio_vigente(None, falhou))
        self.assertIsNone(_bloqueio_vigente(reg, {}))                             # sem sensor não se afirma bloqueio
        m = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8"))
        todos = (m.get("oficiais") or []) + (m.get("plataformas") or [])
        bloq = [o for o in todos if "bloq" in str(o.get("situacao") or "").lower()]
        self.assertLessEqual(len(bloq), 6)                                        # eram 13
        for o in bloq:
            self.assertEqual(o.get("achados") or 0, 0)                            # nenhum bloqueado está entregando editais

    def test_parametros_e_evidencias_no_repositorio(self):
        p = json.loads((ROOT / "config/PARAMETROS-MOTORES-2026-09-09.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(p["parametros"]), 30)
        self.assertTrue(all(x.get("teste_de_aceite") and x.get("medida_de_origem") for x in p["parametros"]))
        r = json.loads((ROOT / "config/REGRAS-CANDIDATAS-MEDIDAS.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(r["regras"]), 8)
        self.assertTrue((ROOT / "biblioteca_alexandria/AUDITORIA-COMPLETA-2026-09-09.md").exists())
        self.assertTrue((ROOT / "biblioteca_alexandria/MAPA-DE-PUBLICACAO-OFICIAL.md").exists())


if __name__ == "__main__":
    unittest.main()
