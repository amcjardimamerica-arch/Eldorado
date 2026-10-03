"""03/10/2026 — teste do motor 19 (editais de institutos e fundações das empresas que já destinam imposto).

Achados do teste: o motor lia só 3 das 30 rotas (limite geral de 3 páginas); o portal captadores.org.br, que reúne os editais
de empresas, era a 30ª rota e nunca era lido; 6 endereços de institutos tinham mudado ou caído; "Prêmio Liga STEAM" (escolas)
virava oportunidade; a notícia "Fundação Maria Emília abre edital…" caía no filtro de pertinência por não repetir "OSC";
"MAPFRE recebe projetos incentivados até 30 de setembro" (encerrado) passaria como candidato. Sem rede."""
import sys, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import sensores as s
from src import empresas_destinadoras as ed

SID = "plat-empresas-editais-incentivados"
CAPT = "https://captadores.org.br/editais/"
# trecho real da listagem de captadores.org.br/editais (03/10/2026)
LISTAGEM = """<article><h2><a href="https://captadores.org.br/editais/fundacao-maria-emilia-abre-edital-com-apoio-de-ate-r-1-milhao-para-projetos-em-saude-e-educacao/" rel="bookmark">Fundação Maria Emília abre edital com apoio de até R$ 1 milhão para projetos em saúde e educação</a></h2>
<p>Post publicado: 4 de setembro de 2026</p><p>A Fundação Maria Emília abriu inscrições para o Edital FME Transforma nº 02/2026, voltado ao financiamento de projetos nas áreas de saúde e educação. As propostas poderão solicitar até R$…</p></article>
<article><h2><a href="https://captadores.org.br/editais/mapfre-recebe-projetos-incentivados-ate-30-de-setembro/" rel="bookmark">MAPFRE recebe projetos incentivados até 30 de setembro</a></h2>
<p>A MAPFRE recebe projetos incentivados de organizações sociais sem fins lucrativos.</p></article>
<article><h2><a href="https://captadores.org.br/editais/zurich-seguros-abre-edital-nacional-para-apoiar-projetos-sociais-via-leis-de-incentivo-fiscal/" rel="bookmark">Zurich Seguros abre edital nacional para apoiar projetos sociais via leis de incentivo fiscal</a></h2>
<p>Organizações sociais com projetos aprovados em leis de incentivo podem se inscrever.</p></article>"""
FAMB = """<a href="https://www.famb.org.br/premio-liga-steam">Prêmio Liga STEAM</a> <p>Prêmio para projetos de educação em escolas públicas
e organizações sociais sem fins lucrativos</p> <a href="https://www.famb.org.br/jornada-liga-steam">Jornada Liga STEAM</a>"""


def sensor():
    return [x for x in s.registro() if x["id"] == SID][0]


class Rotas(unittest.TestCase):
    def test_le_todas_as_rotas_e_o_portal_primeiro(self):
        sen = sensor()
        pags = s._paginas(sen)
        self.assertEqual(pags[0], CAPT)
        self.assertGreaterEqual(sen["max_paginas"], len(pags))          # nenhuma rota fica fora do limite
        self.assertGreaterEqual(len(pags), 30)
        self.assertNotIn("https://www.portoitapoa.com/", pags)

    def test_paginas_de_edital_antes_das_homes(self):
        r = ed.rotas(40)
        homes = r.index("https://www.institutolojasrenner.org.br/")
        self.assertLess(r.index("https://www.institutolojasrenner.org.br/editais-abertos/"), homes)
        self.assertLess(r.index("https://lp.simbi.social/ultra"), homes)

    def test_enderecos_conferidos_e_pendencias(self):
        r = ed.rotas(40)
        for velho in ("https://www.institutonatura.org.br/", "https://alimentacaoemfoco.org.br/", "https://www.fundojbsamazonia.org/",
                      "http://www.viavarejo.com.br/fundacaoviavarejo", "https://www.fundacaoraizen.org.br/"):
            self.assertNotIn(velho, r)
        self.assertIn("https://www.institutonatura.org/", r)
        self.assertIn("https://fundacaotelefonicavivo.org.br/", r)
        b = {x["nome"]: x for e in ed.load_json(ed.SAIDA)["empresas"] for x in e["bracos_sociais"]}
        self.assertIn("DNS", b["Fundação Cargill"]["pendencia"])


class EncerradoNoTitulo(unittest.TestCase):
    def test_prazo_vencido_no_titulo(self):
        h = date(2026, 10, 3)
        self.assertTrue(s._ENCERRADO_NO_TITULO("MAPFRE recebe projetos incentivados até 30 de setembro", h))
        self.assertFalse(s._ENCERRADO_NO_TITULO("Zurich recebe projetos até 19 de outubro", h))
        self.assertFalse(s._ENCERRADO_NO_TITULO("Zurich Seguros abre edital nacional", h))


class Leitura(unittest.TestCase):
    def _ler(self, paginas):
        sen = dict(sensor(), urls=list(paginas))
        with mock.patch.object(s, "_paginas", return_value=list(paginas)), \
                mock.patch.object(s, "_abrir", side_effect=lambda u, **k: (paginas[u], u, 200)), mock.patch.object(s.time, "sleep"):
            return s.ler(sen, pausa=0, data=date(2026, 10, 3))

    def test_portal_maria_emilia_entra_mapfre_encerrado_sai(self):
        r = self._ler({CAPT: LISTAGEM})
        tits = [a["titulo"] for a in r["achados"]]
        self.assertTrue(any("Maria Emília" in t for t in tits), tits)
        self.assertTrue(any("Zurich" in t for t in tits), tits)
        self.assertFalse(any("MAPFRE" in t for t in tits), tits)
        self.assertEqual(r["diagnostico"]["encerrados_no_titulo"], 1)

    def test_liga_steam_vetada(self):
        r = self._ler({"https://www.famb.org.br/": FAMB})
        self.assertEqual(r["achados"], [])
        self.assertEqual(r["diagnostico"]["camada1_vetados"], 2)

    def test_rotas_alem_do_limite_sao_registradas(self):
        sen = dict(sensor(), max_paginas=1)
        pags = {CAPT: LISTAGEM, "https://www.famb.org.br/": FAMB}
        with mock.patch.object(s, "_paginas", return_value=list(pags)), \
                mock.patch.object(s, "_abrir", side_effect=lambda u, **k: (pags[u], u, 200)), mock.patch.object(s.time, "sleep"):
            r = s.ler(sen, pausa=0, data=date(2026, 10, 3))
        self.assertEqual(r["diagnostico"]["paginas_alem_do_limite"], 1)


if __name__ == "__main__":
    unittest.main()
