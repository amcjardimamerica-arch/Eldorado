"""O catálogo tem de guardar o endereço certo, não o nome certo.

O motor de busca do Eldorado vai onde o catálogo manda. Se o catálogo conhece
"BNDES Periferias" mas aponta para a busca do Diário Oficial da União, o motor
procura para sempre no lugar onde a informação não está — e foi exatamente o
que aconteceu com o 6º ciclo, aberto de 18/08/2026 a 04/12/2026 e invisível
para o sistema até 09/09/2026.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/fontes_captacao_260.json"


def catalogo():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def por_id(dados):
    return {f["id"]: f for f in dados["fontes"]}


class TesteEnderecosConfirmados(unittest.TestCase):
    def test_bndes_periferias_aponta_para_a_pagina_da_chamada(self):
        fonte = por_id(catalogo())["captacao-175"]
        self.assertEqual(fonte["sites"][0], "https://www.bndes.gov.br/periferias",
                         "o primeiro endereço tem de ser a página da chamada, não a busca do DOU")

    def test_instituto_lojas_renner_aponta_para_o_edital(self):
        fonte = por_id(catalogo())["captacao-235"]
        self.assertTrue(any("edital-encantando-comunidades" in s for s in fonte["sites"]))

    def test_fontes_novas_da_rodada_entraram(self):
        programas = {f.get("programa") for f in catalogo()["fontes"]}
        for esperado in ("Banco do Nordeste — Editais Sociais (incentivo fiscal)",
                         "Funbio — Programa Biodiversidade Litoral do Paraná",
                         "SECULT Goiás — chamamentos públicos da Lei 13.019/2014"):
            self.assertIn(esperado, programas)

    def test_fonte_de_fluxo_continuo_esta_marcada_como_tal(self):
        # Instituto Impactarte não tem cronograma. Se o coletor tratar como
        # edital, vai inventar prazo — e prazo errado faz perder inscrição.
        fontes = [f for f in catalogo()["fontes"] if "Impactarte" in (f.get("programa") or "")]
        self.assertEqual(len(fontes), 1)
        self.assertIn("fluxo contínuo", fontes[0]["nota"])


class TesteArmadilhas(unittest.TestCase):
    def test_ritmo_do_pncp_esta_registrado(self):
        urls = " ".join(a.get("url", "") for a in catalogo()["armadilhas"])
        self.assertIn("pncp.gov.br/api/consulta", urls)

    def test_portal_de_noticia_marcado_como_fonte_proibida_de_prazo(self):
        arm = [a for a in catalogo()["armadilhas"] if "captadores.org.br" in a.get("url", "")]
        self.assertEqual(len(arm), 1)
        self.assertIn("prazo", arm[0]["motivo"])

    def test_plataformas_privadas_apontam_a_saida_pela_busca_do_pncp(self):
        arm = [a for a in catalogo()["armadilhas"] if "portaldecompraspublicas" in a.get("url", "")]
        self.assertEqual(len(arm), 1)
        self.assertIn("api/search", arm[0]["motivo"])


class TesteIntegridade(unittest.TestCase):
    def test_ids_unicos(self):
        ids = [f["id"] for f in catalogo()["fontes"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_resumo_bate_com_a_lista(self):
        dados = catalogo()
        self.assertEqual(dados["resumo"]["total"], len(dados["fontes"]))

    def test_nenhuma_fonte_estadual_de_goias_recebeu_url_de_outro_estado(self):
        # Guarda contra o erro cometido em 08/09/2026, quando um script colou
        # URL estadual do PNAB em fonte municipal de Goiânia.
        for fonte in catalogo()["fontes"]:
            if fonte.get("uf") == "GO" and fonte.get("nivel") == "municipal":
                for site in fonte.get("sites") or []:
                    self.assertNotIn("pnab.cultura.go.gov.br", site)


if __name__ == "__main__":
    unittest.main()
