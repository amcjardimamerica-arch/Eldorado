"""Teste do motor 17 (CNPq / MCTI / Setec-MEC — extensão e parceria com OSC) de 03/10/2026."""
import json
import unittest
from pathlib import Path
from unittest import mock

from src import sensores as S

ROOT = Path(__file__).resolve().parents[1]
LISTA_CNPQ = """<html><body><div id="content-core"><h2>Busca de Chamadas Abertas para Submissão de Propostas</h2>
<a href="https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao/mai-dai">Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação – MAI/DAI</a>
<a href="https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao/rhae">Chamada Pública CNPq/SETEC/MCTI Nº 29/2026 – RHAE IA – Recursos Humanos em Áreas Estratégicas – bolsas</a>
</div></body></html>"""


class Motor17(unittest.TestCase):
    @staticmethod
    def cfg_url():
        inv = json.loads((ROOT / "config/investigacao.json").read_text(encoding="utf-8"))
        return next(f["url"] for f in inv["fontes"] if f["id"] == "cnpq-extensao")

    def test_rotas_sem_os_enderecos_404(self):
        self.assertEqual(self.cfg_url(), "https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao")
        rotas = [r["url"] for r in S.rotas_alternativas({"id": "plat-cnpq-extensao"})]
        self.assertFalse([u for u in rotas if "acoes-e-programas/programas/chamadas-publicas" in u or "secretaria-de-educacao-profissional" in u])
        self.assertIn("https://www.gov.br/mcti/pt-br/centrais-de-conteudo/comunicados-mcti", rotas)
        self.assertNotIn("https://www.gov.br/mcti/pt-br", rotas)                  # a home do MCTI (2.806 links) saiu

    def test_chamadas_de_pesquisa_sao_vetadas_e_extensao_com_osc_passa(self):
        termos, vetos = S.lexico_camada1({"id": "plat-cnpq-extensao"})
        for rot in ("Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação",
                    "Chamada Pública CNPq Nº 29/2026 – RHAE IA – Recursos Humanos em Áreas Estratégicas"):
            self.assertTrue(S.casa_camada1(rot, termos, vetos)["veto"], rot)
        ok = S.casa_camada1("Chamada Pública MCTI/CNPq de Tecnologia Social e extensão com organizações da sociedade civil", termos, vetos)
        self.assertTrue(ok["passa"]); self.assertFalse(ok["veto"])

    def test_leitura_da_lista_nao_gera_falha_nem_achado_de_pesquisa(self):
        def abrir(url, timeout=12, max_bytes=0):
            return (LISTA_CNPQ if "cnpq" in url else "<html><body>sem chamadas</body></html>"), url, 200
        s = {"id": "plat-cnpq-extensao", "nome": "CNPq", "tipo": "plataforma", "urls": [self.cfg_url()], "territorio": "BR", "busca": None}
        with mock.patch.object(S, "_abrir", side_effect=abrir):
            r = S.ler(s, pausa=0)
        self.assertEqual(r["falhas"], [])
        self.assertEqual(r["achados"], [])
        self.assertGreaterEqual(r["diagnostico"]["camada1_vetados"], 2)


if __name__ == "__main__":
    unittest.main()
