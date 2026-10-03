"""03/10/2026 — teste do motor 16 (Lei Rouanet / SALIC + editais do Ministério da Cultura): janela da IN MinC 29/2026,
leitura da página "inscrições abertas" do MinC com prazo de cada edital, vetos (eleição, pareceristas), publicado × lido
(edital listado e não lido → paginas_nao_lidas → maestro "parcial") e corte da API do SALIC pelo limite. Sem rede."""
import sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import rouanet_salic as rs
from src import maestro

ORIG = rs.projetos

HOJE = date(2026, 10, 3)
BASE = "https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/"
# trecho real dos cartões da página do MinC (03/10/2026)
LISTAGEM = (
    '<div class="govbr-cards"><a class="govbr-card-content" href="' + BASE + 'programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2">'
    ' <span class="front"> <span class="titulo">Programa Rouanet nas Favelas 2</span></span></a>'
    '<a class="govbr-card-content" href="' + BASE + 'biblioteca-comunitaria-e-cultura-viva"> <span class="front"> <span class="titulo">'
    'Edital Biblioteca Comunitária é Cultura Viva</span></span></a>'
    '<a class="govbr-card-content" href="' + BASE + 'rouanet-centro-oeste"> <span class="titulo">Programa Rouanet Centro-Oeste</span></a>'
    '<a class="govbr-card-content" href="' + BASE + 'eleicao-cnpc"> <span class="titulo">Eleição do CNPC 2026</span></a>'
    '<a class="govbr-card-content" href="' + BASE + 'pareceristas"> <span class="titulo">Credenciamento de Pareceristas</span></a>'
    '<a class="govbr-card-content" href="' + BASE + 'programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2"> repetido </a>'
    '<a href="https://www.gov.br/cultura/pt-br/assuntos/noticias">Notícias</a></div>')
PAGINAS = {
    BASE + "programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2":
        "<p>Início das inscrições no sistema Salic 15/08/2026 Encerramento do prazo de inscrição 13/10/2026, às 23h59min59s "
        "Divulgação do resultado provisório Até 27/11/2026</p>",
    BASE + "biblioteca-comunitaria-e-cultura-viva": "<p>As inscrições são permanentes (fluxo contínuo).</p>",
    BASE + "rouanet-centro-oeste": "<p>Período para propostas inscritas: até 20/8/2026. Resultado provisório até 27/10/2026.</p>",
    BASE + "eleicao-cnpc": "<p>Inscrições até 30/10/2026.</p>",
    BASE + "pareceristas": "<p>Inscrições até 31/12/2026.</p>",
}


def getter(falhar=()):
    def g(url):
        if url == rs.EDITAIS:
            return LISTAGEM
        if url in falhar:
            raise TimeoutError("tempo esgotado")
        return PAGINAS[url]
    return g


class Janela(unittest.TestCase):
    def test_aberta_hoje_com_28_dias(self):
        j = rs.janela(HOJE)
        self.assertEqual((j["aberta"], j["fim"], j["dias_restantes"]), (True, "2026-10-31", 28))

    def test_fechada_depois_de_31_10_aponta_a_proxima(self):
        j = rs.janela(date(2026, 11, 5))
        self.assertEqual((j["aberta"], j["inicio"]), (False, "2027-02-01"))


class EditaisMinc(unittest.TestCase):
    def test_listagem_um_por_edital_sem_menu(self):
        e = rs.editais_da_listagem(LISTAGEM)
        self.assertEqual(len(e), 5)
        self.assertEqual(e[0]["titulo"], "Programa Rouanet nas Favelas 2")

    def test_prazo_de_inscricao_e_nao_o_resultado(self):
        p = rs.prazo_do_edital(rs._texto(PAGINAS[BASE + "programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2"]))
        self.assertEqual((p["fim"], p["fluxo_continuo"]), ("2026-10-13", False))

    def test_vereditos(self):
        d = {"fontes": {}}
        r = {x["titulo"]: x for x in rs.editais_minc(HOJE, d, getter())}
        self.assertEqual(r["Programa Rouanet nas Favelas 2"]["veredito"], "OPORTUNIDADE")
        self.assertEqual(r["Edital Biblioteca Comunitária é Cultura Viva"]["veredito"], "OPORTUNIDADE")
        self.assertTrue(r["Edital Biblioteca Comunitária é Cultura Viva"]["fluxo_continuo"])
        self.assertEqual((r["Programa Rouanet Centro-Oeste"]["veredito"], r["Programa Rouanet Centro-Oeste"]["fim"]),
                         ("ACOMPANHAR", "2026-08-20"))
        self.assertEqual(r["Eleição do CNPC 2026"]["veredito"], "RUIDO")
        self.assertEqual(r["Credenciamento de Pareceristas"]["veredito"], "RUIDO")
        self.assertEqual(d["fontes"]["editais_minc"], {"listados": 5, "lidos": 5})
        self.assertNotIn("paginas_nao_lidas", d)

    def test_sem_prazo_legivel_vira_acompanhar(self):
        r = rs.classificar_edital({"titulo": "MICSUL 2026", "fim": None, "fluxo_continuo": False}, HOJE)
        self.assertEqual(r["veredito"], "ACOMPANHAR")

    def test_edital_nao_lido_vira_parcial(self):
        d = {"fontes": {}}
        with mock.patch.object(rs.time, "sleep"):
            out = rs.editais_minc(HOJE, d, getter(falhar={BASE + "rouanet-centro-oeste"}))
        self.assertEqual(len(out), 4)
        self.assertIn("Programa Rouanet Centro-Oeste", d["paginas_nao_lidas"][0])
        self.assertEqual(maestro.cobertura(rs.MOTOR_ID, {"cor": "azul", "falhas": 0}, {}, d), "parcial")


class LerMotor(unittest.TestCase):
    def _rodar(self, corte=False):
        tmp = Path(tempfile.mkdtemp())
        lote = [{"PRONAC": i, "cgccpf": "12.345.678/0001-90", "nome": "P"} for i in range(100)]

        def api(url, *a, **k):
            return {"_embedded": {"projetos": lote if corte else lote[:7]}}
        with mock.patch.object(rs, "ESTADO", tmp / "salic_go.json"), mock.patch.object(rs, "ARQ", tmp / "arq"), \
                mock.patch.object(rs, "_get_json", side_effect=api), mock.patch.object(rs, "_get_texto", side_effect=getter()), \
                mock.patch.object(rs.time, "sleep"), mock.patch.object(rs, "projetos", side_effect=lambda uf, ano: ORIG(uf, ano, limite=200, pausa=0)):
            return rs.ler_motor(hoje=HOJE)

    def test_achados_janela_mais_editais_abertos(self):
        r = self._rodar()
        tits = [a["titulo"] for a in r["achados"]]
        self.assertEqual(len(tits), 3)
        self.assertTrue(tits[0].startswith("Lei Rouanet"))
        self.assertIn("Ministério da Cultura — Programa Rouanet nas Favelas 2", tits)
        self.assertNotIn("cobertura_cortada", r["diagnostico"])

    def test_limite_do_salic_vira_cobertura_cortada(self):
        r = self._rodar(corte=True)
        self.assertTrue(any("SALIC GO 2026" in x for x in r["diagnostico"]["cobertura_cortada"]))
        self.assertEqual(maestro.cobertura(rs.MOTOR_ID, {"cor": "azul", "falhas": 0}, {}, r["diagnostico"]), "parcial")


if __name__ == "__main__":
    unittest.main()
