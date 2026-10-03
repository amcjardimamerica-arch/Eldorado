"""03/10/2026 — teste do motor 10 (MPU): FDD sem alarme falso (texto visível, sem script), alerta que não some entre
leituras, outra regional/estado do MPT, publicado × lido nas listagens (paginação e paginas_nao_lidas) e feed parado. Sem rede."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import ministerios_publicos as mp
from src import maestro

HOJE = date(2026, 10, 3)
# estrutura real da página do FDD (gov.br, 03/10/2026): o título e o "Não há" separados por ~2 mil caracteres de script
FDD_HTML = ("<html><head><title>Seleção em andamento</title></head><body><nav>Assuntos Seus Direitos Consumidor Direitos Difusos "
       "Seleções em Andamento</nav><h1>Seleção em andamento</h1><script>" + "$(tile).children('.tile-subtitle'); " * 80 +
       "</script><p>Publicado em 23/10/2023 11h33 Atualizado em 08/07/2026 15h30</p><div>Não há</div></body></html>")


class FDD(unittest.TestCase):
    def test_nao_ha_com_script_no_meio(self):
        sem_limpeza = mp.selecao_sem_edital(mp.re.sub(r"<[^>]+>", " ", FDD_HTML))
        self.assertFalse(sem_limpeza)                                # o defeito: o motor via seleção aberta
        self.assertTrue(mp.selecao_sem_edital(mp.texto_visivel(FDD_HTML)))  # a correção

    def test_alerta_verdadeiro_continua(self):
        aberta = FDD_HTML.replace("<div>Não há</div>", "<div>Edital de Chamada Pública nº 1/2026 — inscrições até 30/11/2026</div>")
        self.assertFalse(mp.selecao_sem_edital(mp.texto_visivel(aberta)))


class OutraRegional(unittest.TestCase):
    def test_outros_estados(self):
        for t in ("Cadastro de órgãos e entidades de ES para solicitação de bens e recursos oriundos de reversões",
                  "MPT/AL destina recursos para aquisição de veículos", "MPT-PA/AP lança edital com novas regras",
                  "MPT-MT abre cadastro para entidades", "PRT 23ª Região — edital"):
            self.assertTrue(mp.outra_regional(t), t)

    def test_goias_e_nacional_nao_sao_outra_regional(self):
        for t in ("Cadastro de órgãos e entidades para solicitação de bens e recursos oriundos de reversões",
                  "MPT-GO abre cadastro", "PRT 18ª Região — edital de destinação", "valor de R$ 50 mil"):
            self.assertFalse(mp.outra_regional(t), t)


class PublicadoLido(unittest.TestCase):
    def test_lacuna(self):
        p1 = [{"data_publicacao": d} for d in ("2026-10-02", "2026-09-30", "2026-09-29")]
        self.assertTrue(mp.lacuna_da_listagem(p1, "2026-09-20"))     # página toda mais nova que a última leitura
        self.assertFalse(mp.lacuna_da_listagem(p1, "2026-09-29"))
        self.assertFalse(mp.lacuna_da_listagem(p1, None))            # primeira leitura: não há como medir

    def test_data_de_cada_link_e_a_dele(self):
        h = ('<li><a href="/n/9">MPF em Goiás cadastra entidades</a> 25/09/2026</li>'
             '<li><a href="/n/8">Outra notícia antiga do MPF</a> 15/09/2026</li><li><a href="/n/7">Mais uma antiga aqui</a> 10/09/2026</li>')
        self.assertEqual([l["data_publicacao"] for l in mp.links_da_listagem(h, "https://x.mp.br/")], ["2026-09-25", "2026-09-15", "2026-09-10"])

    def test_feed_parado(self):
        self.assertTrue(mp.feed_parado([{"data_publicacao": "2026-07-28"}, {"data_publicacao": "2026-07-13"}], HOJE))
        self.assertFalse(mp.feed_parado([{"data_publicacao": "2026-09-17"}], HOJE))

    def _ler(self, pagina2_ok):
        d = Path(tempfile.mkdtemp())
        cfg = {"fontes": [{"id": "f15", "orgao": "MPF", "unidade": "PR-GO", "modo": "listagem_html",
                           "url": "https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias", "paginacao": "?b_start:int={offset}", "passo": 10,
                           "max_paginas": 1}],
               "cadencia_dias": {"listagem_html": 7}, "lexico_alvo": ["bens e valores"], "registros_fixos": [], "pausa_segundos": 0}
        (d / "cfg.json").write_text(json.dumps(cfg), encoding="utf-8")
        (d / "est.json").write_text(json.dumps({"ultima_por_fonte": {"f15": "2026-09-20"}, "inventario": {"inventario_base_registrado": True}}),
                                    encoding="utf-8")
        p1 = "".join(f'<li><a href="/n/{i}">Notícia número {i} do MPF em Goiás</a> {i:02d}/10/2026</li>' for i in (1, 2, 3)) \
            .replace("01/10", "30/09")
        p2 = '<li><a href="/n/9">MPF em Goiás cadastra entidades para receber bens e valores</a> 25/09/2026</li>' \
             '<li><a href="/n/8">Outra notícia antiga do MPF</a> 15/09/2026</li><li><a href="/n/7">Mais uma antiga</a> 10/09/2026</li>'

        def abrir(url, cfg_, *a, **k):
            if "b_start" in url:
                if not pagina2_ok:
                    return p1.encode()                                # a página 2 não alcança (mesmo conteúdo novo)
                return p2.encode()
            return p1.encode()
        with mock.patch.object(mp, "CFG", d / "cfg.json"), mock.patch.object(mp, "ESTADO", d / "est.json"), \
             mock.patch.object(mp, "_abrir", side_effect=abrir):
            r = mp.ler_motor(hoje=HOJE)
            est = json.loads((d / "est.json").read_text(encoding="utf-8"))
        return r, est

    def test_pagina_seguinte_cobre_o_intervalo(self):
        r, est = self._ler(True)
        self.assertNotIn("paginas_nao_lidas", r["diagnostico"])
        self.assertEqual(r["diagnostico"]["fontes"]["f15"]["paginas_extras"], 1)
        self.assertEqual(est["ultima_por_fonte"]["f15"], "2026-10-03")
        self.assertTrue(any("bens e valores" in a["titulo"] for a in est["acompanhar"]))   # o item da página 2 foi lido

    def test_intervalo_nao_coberto_vira_parcial_e_nao_avanca(self):
        r, est = self._ler(False)
        self.assertIn("f15 MPF", r["diagnostico"]["paginas_nao_lidas"][0])
        self.assertEqual(est["ultima_por_fonte"]["f15"], "2026-09-20")
        self.assertEqual(maestro.cobertura("mpu-destinacao", {"cor": "azul", "falhas": 0}, {}, r["diagnostico"]), "parcial")


class Catalogo(unittest.TestCase):
    def test_rotas_corrigidas(self):
        c = {f["id"]: f for f in json.loads((ROOT / "config/ministerios_publicos.json").read_text(encoding="utf-8"))["fontes"]}
        self.assertIn("search_rss", c["f12"]["url"]); self.assertEqual(c["f33"]["modo"], "ruido_conhecido")
        self.assertEqual(c["f15"]["paginacao"], "?b_start:int={offset}")


if __name__ == "__main__":
    unittest.main()
