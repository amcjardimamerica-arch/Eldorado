"""03/10/2026 — teste do motor 06 (Congresso Nacional): comunicados da CMO com href relativo e data dentro do link,
situação do PLOA pelo "Último estado" (não pelo menu), regime jurídico das associações, e PUBLICADO × LIDO nas notícias
(feed curto → listagem paginada → paginas_nao_lidas). Sem rede."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import congresso_nacional as cn
from src import maestro

HOJE = date(2026, 10, 3)
CFG = json.loads((ROOT / "config/congresso_nacional.json").read_text(encoding="utf-8"))
PAG = "https://www.congressonacional.leg.br/web/cmo/comunicados"
# trecho real da página da CMO (03/10/2026)
TABELA = ('<table class="table table-bordered table-hover table-striped"> <tbody class="table-data"> <tr> <td> '
          '<a href="comunicados/-/blogs/materias-novas-relatorios-entregues-e-prazo-de-emendas"> 02/10/2026 12:35<br/> '
          '<span style="color: black;">Matérias Novas/Relatórios Entregues e prazo de emendas</span> </a><br> </td> </tr> <tr> <td> '
          '<a href="comunicados/-/blogs/loa-2027-instrucoes-do-lexor"> 30/09/2026 02:53<br/> <span style="color: black;">LOA 2027 - '
          'Instruções do Lexor</span> </a><br> </td> </tr> <tr> <td> <a href="comunicados/-/blogs/orientacoes-oficio-de-apoio-a-emenda-'
          'parlamentar"> 07/09/2026 02:00<br/> <span style="color: black;">Orientações - Ofício de Apoio à Emenda Parlamentar (LexEdit)'
          '</span> </a><br> </td> </tr> <tr> <td> <a href="comunicados/-/blogs/confirmada-reuniao"> 22/06/2026 03:52<br/> '
          '<span style="color: black;">Confirmada Reunião de Líderes</span> </a><br> </td> </tr> </tbody> </table>')
LOA = ('<nav>Matérias Bicamerais Matérias Aguardando Sanção Acompanhamento de Matérias</nav> <p>PLN 24/2026</p>'
       '<table><tr><td>Apresentação do projeto de lei orçamentária</td><td>Em andamento</td></tr>'
       '<tr><td>Apresentação de emendas</td><td>Não iniciada</td></tr></table>'
       '<p><strong>Ementa:</strong> <span>Estima a receita e fixa a despesa da União para o exercício financeiro de 2027.</span></p>'
       '<p><strong>Último estado:</strong> <span>31/08/2026 - AGUARDANDO DESPACHO</span> </p> <div>Comunicados</div>')


def rss(itens):
    corpo = "".join(f"<item><title>{t}</title><link>{u}</link><description></description><pubDate>{d}</pubDate></item>"
                    for t, u, d in itens)
    return f'<?xml version="1.0"?><rss><channel>{corpo}</channel></rss>'


class Comunicados(unittest.TestCase):
    def test_href_relativo_e_data_dentro_do_link(self):
        c = cn.comunicados_da_pagina(TABELA, PAG)
        self.assertEqual(len(c), 4)
        self.assertEqual(c[0]["url"], PAG + "/-/blogs/materias-novas-relatorios-entregues-e-prazo-de-emendas")
        self.assertEqual((c[0]["publicado"], c[0]["titulo"]), ("2026-10-02", "Matérias Novas/Relatórios Entregues e prazo de emendas"))
        self.assertEqual(c[2]["titulo"], "Orientações - Ofício de Apoio à Emenda Parlamentar (LexEdit)")

    def test_comunicados_da_janela_viram_acompanhar(self):
        dentro = [x for x in cn.comunicados_da_pagina(TABELA, PAG) if x["publicado"] >= "2026-08-04"]
        self.assertEqual(len(dentro), 3)
        for x in dentro:
            self.assertEqual(cn.classificar_item(x, HOJE, CFG)["veredito"], "ACOMPANHAR", x["titulo"])


class SituacaoDoPloa(unittest.TestCase):
    def test_ultimo_estado_e_nao_o_menu(self):
        e = cn.etapa_emendas(LOA)
        self.assertEqual((e["status"], e["situacao"], e["situacao_desde"], e["projeto"]),
                         ("nao_iniciada", "Aguardando despacho", "2026-08-31", "PLN 24/2026"))


class Proposicoes(unittest.TestCase):
    def c(self, ementa):
        return cn.classificar_item({"fonte": "B", "titulo": "PL", "ementa": ementa}, HOJE, CFG)

    def test_regime_juridico_das_associacoes(self):
        r = self.c("Dispõe sobre o regime jurídico específico das associações civis sem fins lucrativos de utilidade pública que "
                   "instituam sistemas de beneficência e assistência mútua de interesse social.")
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "regra_para_entidades"))

    def test_protecao_patrimonial_nao_e_osc(self):
        r = self.c("Altera a Lei Complementar nº 213 para instituir regime jurídico próprio, proporcional e autogerido para as "
                   "associações de proteção patrimonial mutualista, e dá outras providências.")
        self.assertEqual(r["veredito"], "RUIDO")

    def test_ibs_cbs_das_entidades_continua(self):
        r = self.c("Altera a Lei Complementar nº 214 para dispor sobre a não incidência do IBS e da CBS no âmbito das entidades civis "
                   "sem fins lucrativos")
        self.assertEqual((r["veredito"], r["categoria"]), ("ACOMPANHAR", "tributario_entidades"))


class NoticiasPublicadoLido(unittest.TestCase):
    CAMARA_LIST = ('<h3><a href="https://www.camara.leg.br/noticias/1306708-projeto-inclui-policias-penais">Projeto inclui policias '
                   'penais no SUSP</a></h3> <span class="g-chamada__data">29/09/2026 11:20</span>'
                   '<h3><a href="https://www.camara.leg.br/noticias/1306600-outra-noticia-antiga">Outra noticia antiga da Camara</a></h3>'
                   ' <span class="g-chamada__data">27/09/2026 09:00</span>')

    def test_listagens_das_duas_casas(self):
        c = cn.noticias_da_listagem(self.CAMARA_LIST, "Câmara dos Deputados", "https://www.camara.leg.br/noticias/ultimas?pagina=1")
        self.assertEqual([x["publicado"] for x in c], ["2026-09-29", "2026-09-27"])
        s = cn.noticias_da_listagem('<a href="/noticias/materias/2026/09/28/chega-ao-congresso-projeto"> <span>Chega ao Congresso '
                                    'projeto que torna crime</span> </a>', "Senado Federal", "https://www12.senado.leg.br/noticias/ultimas/3")
        self.assertEqual((s[0]["url"], s[0]["publicado"]),
                         ("https://www12.senado.leg.br/noticias/materias/2026/09/28/chega-ao-congresso-projeto", "2026-09-28"))

    def _fonte_d(self, ultima, listagem_ok):
        cfg = {"noticias": {"janela_dias": 15, "feeds": [{"casa": "Câmara dos Deputados", "url": "https://www.camara.leg.br/rss",
                                                        "listagem": "https://www.camara.leg.br/noticias/ultimas?pagina={pagina}",
                                                        "max_paginas_recuperacao": 2}]}, "ritmo": {"pausa_segundos": 0}}
        feed = rss([("Hoje", "https://www.camara.leg.br/noticias/1306900-hoje", "Fri, 02 Oct 2026 22:27:00 GMT"),
                    ("Ontem", "https://www.camara.leg.br/noticias/1306800-ontem", "Thu, 01 Oct 2026 15:50:00 GMT")])

        def rede(url, *a, **k):
            if url.endswith("/rss"):
                return feed
            if listagem_ok:
                return self.CAMARA_LIST
            raise RuntimeError("tempo esgotado")
        diag = {"fontes": {"D": {"falhas": [], "consultas": 0, "itens": 0}},
                "_estado": {"noticias_lidas_ate": {"Câmara dos Deputados": ultima}}}
        with mock.patch.object(cn, "_get_texto", side_effect=rede), mock.patch.object(cn.time, "sleep"):
            itens = cn.fonte_d(HOJE, cfg, diag)
        return itens, diag["fontes"]["D"]

    def test_sem_buraco_nao_le_listagem(self):
        itens, F = self._fonte_d("2026-10-01", True)
        self.assertEqual((len(itens), F["consultas"], F["lidas_ate"]["Câmara dos Deputados"]), (2, 1, "2026-10-02"))

    def test_buraco_coberto_pela_listagem(self):
        itens, F = self._fonte_d("2026-09-28", True)
        self.assertEqual(len(itens), 4); self.assertTrue(F["recuperadas"]); self.assertNotIn("paginas_nao_lidas", F)

    def test_buraco_nao_coberto_vira_parcial(self):
        _itens, F = self._fonte_d("2026-09-28", False)
        self.assertIn("feed curto", F["paginas_nao_lidas"][0])
        self.assertEqual(F["lidas_ate"]["Câmara dos Deputados"], "2026-09-28")      # não avança: a próxima passagem tenta de novo
        self.assertEqual(maestro.cobertura(cn.MOTOR_ID, {"cor": "azul", "falhas": 0}, {}, {"paginas_nao_lidas": F["paginas_nao_lidas"]}),
                         "parcial")


if __name__ == "__main__":
    unittest.main()
