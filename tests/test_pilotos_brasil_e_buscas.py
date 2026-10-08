"""Parecer dos pilotos (02/10/2026): buscas que não travam na 2ª, página oficial no território certo, retentativa do que
falhou por rede, sede no Brasil (computador/VM) com troca automática e mescla do estado do Interceptador. Sem rede."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from src import piloto_busca as B
from src import pilotos_sede as S
from src import sites_oficiais as SO

ROOT = Path(__file__).resolve().parents[1]


class Buscas(unittest.TestCase):
    def setUp(self):
        B._DDG_NO_VOO.update({"usadas": 0, "bloqueado": False}); B._PONTE_NO_VOO["usadas"] = 0
        self.tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.tmp, True)
        for nome, alvo in (("CACHE_BUSCAS", "cache.json"), ("VIAS", "vias.json")):
            p = mock.patch.object(B, nome, self.tmp / alvo); p.start(); self.addCleanup(p.stop)
        p = mock.patch.object(B.time, "sleep", lambda s: None); p.start(); self.addCleanup(p.stop)

    def test_esgotado_o_duckduckgo_vai_a_api_antes_do_google_noticias(self):
        """Antes: com a chave do Brave gravada, depois de 2 buscas o voo ia direto ao Google Notícias."""
        B._DDG_NO_VOO["usadas"] = 2
        with mock.patch.dict(os.environ, {"BRAVE_SEARCH_KEY": "k"}, clear=False), \
             mock.patch.object(B, "_por_api", lambda n, c, t: [{"titulo": "Edital", "url": "https://x.go.gov.br/e", "buscador": n}] if n == "brave" else []), \
             mock.patch.object(B, "_google_noticias", lambda *a: self.fail("não devia chegar ao Google Notícias")):
            r = B.buscar("edital cultura goiás")
        self.assertEqual(r[0]["buscador"], "brave")

    def test_sem_chave_vai_a_ponte_e_depois_ao_google_noticias(self):
        B._DDG_NO_VOO["bloqueado"] = True
        env = {k: v for k, v in os.environ.items() if k not in ("BRAVE_SEARCH_KEY", "GOOGLE_CSE_KEY")}
        with mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(B, "_ddg_pela_ponte", lambda c, t: []), \
             mock.patch.object(B, "_google_noticias", lambda c, m, t: [{"titulo": "n", "url": "https://news/x", "buscador": "google_noticias"}]):
            self.assertEqual(B.buscar("x")[0]["buscador"], "google_noticias")
        self.assertEqual(B._PONTE_NO_VOO["usadas"], 1)

    def test_no_brasil_a_cota_do_duckduckgo_e_de_30(self):
        B._DDG_NO_VOO["usadas"] = 5
        pedidos = []

        class R:
            headers = {}
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return b'<a class="result__a" href="https://anapolis.go.gov.br/edital">Edital da cultura</a>'
        with mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": "1"}, clear=False), \
             mock.patch.object(B.urllib.request, "urlopen", lambda req, timeout=0: (pedidos.append(req.full_url), R())[1]):
            r = B.buscar("fundo municipal de cultura anápolis")
        self.assertTrue(any("duckduckgo" in u for u in pedidos))
        self.assertEqual(r[0]["url"], "https://anapolis.go.gov.br/edital")

    def test_cache_de_24h_no_voo_real(self):
        chamadas = []
        with mock.patch.dict(os.environ, {"ELDORADO_VOO_REAL": "1"}, clear=False), \
             mock.patch.object(B, "_buscar_sem_cache", lambda c, m, t, mo: (chamadas.append(c), [{"titulo": "a", "url": "https://a"}])[1]):
            B.buscar("financiamento de projetos voluntariado osc 2026")
            r = B.buscar("Financiamento de projetos voluntariado OSC 2026")       # mesma consulta: não gasta busca
        self.assertEqual(len(chamadas), 1)
        self.assertTrue(r[0]["do_cache"])


class Territorio(unittest.TestCase):
    def test_territorio_do_titulo(self):
        self.assertEqual(SO.territorio({"titulo": "Prefeitura de Cachoeira Alta — Edital nº 001/2026 — Goiás / Cachoeira Alta"}),
                         {"uf": "GO", "municipio": "Cachoeira Alta"})
        self.assertEqual(SO.territorio({"titulo": "Prefeitura (município a confirmar) — Edital nº 004/2026 — Goiás"})["municipio"], None)
        self.assertEqual(SO.territorio({"titulo": "x", "municipio": "GO/Goiânia"}), {"uf": "GO", "municipio": "Goiânia"})

    def test_recusa_outro_estado_e_outro_municipio(self):
        """Casos reais de 01–02/10: Cachoeira Paulista (SP) por Cachoeira Alta (GO); SME de Goiânia por Nova Iguaçu de Goiás."""
        t = SO.territorio({"titulo": "Prefeitura de Cachoeira Alta — Edital nº 001/2026 — Goiás / Cachoeira Alta"})
        self.assertIn("outro estado", SO.fora_do_territorio("https://cachoeirapaulista.sp.gov.br/home/avisos/edital", "", t))
        t2 = SO.territorio({"titulo": "Prefeitura de Nova Iguaçu de Goiás — Edital nº 001/2026 — Goiás / Nova Iguaçu de Goiás"})
        self.assertIn("outro município", SO.fora_do_territorio("https://sme.goiania.go.gov.br/x.pdf", "escolha de diretores em Goiânia", t2))
        self.assertIsNone(SO.fora_do_territorio("https://www.novaiguacudegoias.go.gov.br/edital", "", t2))
        self.assertIsNone(SO.fora_do_territorio("https://goias.gov.br/cultura/pnab/", "", t2))      # estadual de Goiás: pode
        ok, porque = SO.validar("https://cachoeirapaulista.sp.gov.br/edital", "edital inscrições prazo regulamento cachoeira", "Edital 001", [], t)
        self.assertFalse(ok); self.assertIn("outro estado", porque)

    def test_site_municipal_pelo_catalogo_ou_padrao(self):
        self.assertEqual(SO.site_municipal({"uf": "GO", "municipio": "Goiânia"}), "goiania.go.gov.br")
        self.assertEqual(SO.site_municipal({"uf": "GO", "municipio": "Cachoeira Alta"}), "cachoeiraalta.go.gov.br")
        self.assertIsNone(SO.site_municipal({"uf": "SP", "municipio": "Campinas"}))

    def test_pagina_guardada_de_outro_estado_nao_e_reusada(self):
        from src import investigador as I
        e = {"titulo": "Prefeitura de Cachoeira Alta — Edital nº 001/2026 — Goiás / Cachoeira Alta",
             "pagina_oficial": "https://cachoeirapaulista.sp.gov.br/home/avisos/x"}
        with mock.patch.object(SO, "descobrir", lambda *a: (None, "nenhuma", {})):
            url, como = I.pagina_oficial(None, e)
        self.assertIsNone(url)
        self.assertIn("outro estado", e["paginas_recusadas"][0]["porque"])


class Retentativa(unittest.TestCase):
    def test_causa(self):
        from src.interceptador import causa_de_retentativa
        self.assertEqual(causa_de_retentativa({"erro": "nenhuma fonte legível"}, {}), "fonte_ilegivel")
        self.assertEqual(causa_de_retentativa({"pagina_oficial": None}, {"busca_do_oficial": {"tentativas": [{"rota": "a", "resultados": 0}, {"validou": "x"}]}}),
                         "busca_sem_resultado")
        self.assertIsNone(causa_de_retentativa({"pagina_oficial": "https://x"}, {}))

    def test_brasil_pega_primeiro_o_que_a_nuvem_nao_leu(self):
        from src import interceptador as I
        feitos = {"a": {"em": "2026-10-02T10:00", "retentar": {"causa": "fonte_ilegivel", "onde": "brasil", "desde": "2026-10-02", "ultima_rota": "nuvem"}},
                  "b": {"em": "2026-10-01T10:00", "retentar": {"causa": "busca_sem_resultado", "onde": "qualquer", "desde": "2026-09-28", "ultima_rota": "nuvem"}},
                  "c": {"em": "2026-10-02T10:00", "qualidade": "parcial"}}
        with mock.patch.object(I, "registro", lambda i: {"titulo": f"edital {i}", "url": f"https://{i}"}):
            with mock.patch.dict(os.environ, {"ELDORADO_LOCAL_BR": "1"}, clear=False):
                self.assertEqual(I.retentativa(feitos, "2026-10-02")["id"], "b")        # o mais antigo primeiro
                f2 = dict(feitos); f2.pop("b")
                self.assertEqual(I.retentativa(f2, "2026-10-02")["id"], "a")
            env = {k: v for k, v in os.environ.items() if k != "ELDORADO_LOCAL_BR"}
            with mock.patch.dict(os.environ, env, clear=True):
                self.assertEqual(I.retentativa(feitos, "2026-10-02")["id"], "b")        # nuvem: só busca, depois de 3 dias
                self.assertIsNone(I.retentativa({"a": feitos["a"]}, "2026-10-02"))     # fonte ilegível é do Brasil


class Sede(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.tmp, True)
        for nome, alvo in (("BATIMENTO", "sede.json"), ("CFG", "cfg.json"), ("INTERCEPTADOR", "interceptador")):
            p = mock.patch.object(S, nome, self.tmp / alvo); p.start(); self.addCleanup(p.stop)
        (self.tmp / "cfg.json").write_text(json.dumps({"sede": "automatica", "minutos_batimento": 45}), encoding="utf-8")

    @__import__('unittest').mock.patch('src.pilotos_sede.dentro_da_janela', return_value=(True, 'teste'))   # 08/10: a janela é testada à parte
    def test_troca_automatica(self, _janela=None):
        agora = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
        self.assertTrue(S.nuvem_deve_voar("interceptador", agora)[0])                    # ninguém no Brasil
        S.batimento("vm", ["interceptador", "espiao"], agora=agora - timedelta(minutes=10))
        voar, motivo = S.nuvem_deve_voar("interceptador", agora)
        self.assertFalse(voar); self.assertIn("vm", motivo)
        voar, motivo = S.nuvem_deve_voar("interceptador", agora + timedelta(minutes=50))  # batimento parou: nuvem reassume
        self.assertTrue(voar); self.assertIn("reassume", motivo)
        S.batimento("computador", ["espiao"], agora=agora)
        self.assertTrue(S.nuvem_deve_voar("interceptador", agora)[0])                    # o computador só roda o Espião
        S.batimento("computador", ["interceptador"], estado="encerrado", agora=agora)
        self.assertTrue(S.nuvem_deve_voar("interceptador", agora)[0])
        (self.tmp / "cfg.json").write_text(json.dumps({"sede": "nuvem"}), encoding="utf-8")
        S.batimento("vm", ["interceptador"], agora=agora)
        self.assertTrue(S.nuvem_deve_voar("interceptador", agora)[0])

    def test_mescla_nao_apaga_o_que_o_outro_gravou(self):
        dest = self.tmp / "interceptador"; (dest / "relatorios").mkdir(parents=True)
        (dest / "estado.json").write_text(json.dumps({"feitos": {"a": {"em": "2026-10-02T10:00", "q": "nuvem"}, "b": {"em": "2026-10-02T12:00", "q": "nuvem"}},
                                                      "rodadas": [{"em": "2026-10-02T12:00", "id": "b"}]}), encoding="utf-8")
        (dest / "relatorios/2026-10-02.json").write_text(json.dumps({"voos": [{"em": "2026-10-02T12:00", "id": "b"}]}), encoding="utf-8")
        (dest / "aguardando.json").write_text("{}", encoding="utf-8")
        copia = self.tmp / "copia"; (copia / "relatorios").mkdir(parents=True)
        (copia / "estado.json").write_text(json.dumps({"feitos": {"a": {"em": "2026-10-02T11:00", "q": "brasil"}, "b": {"em": "2026-10-02T09:00", "q": "velho"}},
                                                       "rodadas": [{"em": "2026-10-02T11:00", "id": "a"}]}), encoding="utf-8")
        (copia / "relatorios/2026-10-02.json").write_text(json.dumps({"voos": [{"em": "2026-10-02T11:00", "id": "a"}]}), encoding="utf-8")
        S.mesclar_interceptador(copia, dest)
        e = json.loads((dest / "estado.json").read_text(encoding="utf-8"))
        self.assertEqual((e["feitos"]["a"]["q"], e["feitos"]["b"]["q"]), ("brasil", "nuvem"))      # vence o mais recente
        self.assertEqual([r["id"] for r in e["rodadas"]], ["a", "b"])
        self.assertEqual(len(json.loads((dest / "relatorios/2026-10-02.json").read_text(encoding="utf-8"))["voos"]), 2)
        self.assertFalse((dest / "aguardando.json").exists())


class Integracao(unittest.TestCase):
    def test_nuvem_confere_a_sede_e_mescla(self):
        w = (ROOT / ".github/workflows/interceptador.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.pilotos_sede nuvem-deve-voar interceptador", w)
        self.assertIn("needs.sede.outputs.voar == 'true'", w)
        self.assertIn("mesclar-interceptador", w)
        self.assertNotIn("rm -rf estado/interceptador", w)
        self.assertIn("BRAVE_SEARCH_KEY", w)
        p = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.pilotos_sede nuvem-deve-voar espiao", p)
        cfg = json.loads((ROOT / "config/pilotos_sede.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["sede"], "automatica")
        for arq in ("scripts/pilotos_brasil.py", "scripts/agendar_pilotos_brasil.ps1", "scripts/agendar_pilotos_brasil.bat", "scripts/instalar_vm_pilotos.sh"):
            self.assertTrue((ROOT / arq).exists(), arq)


if __name__ == "__main__":
    unittest.main()



class JanelaDeVoo(__import__("unittest").TestCase):
    """08/10: os Pilotos só voam na janela de sucesso (config/parametros_pilotos.json › janelas_de_voo)."""
    def test_janela(self):
        from datetime import datetime, timezone
        from src.pilotos_sede import dentro_da_janela as J, nuvem_deve_voar as N
        d = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)   # noqa: E731
        self.assertTrue(J("espiao", d("2026-10-08T13:00:00"))[0])          # quinta, 10h BRT
        self.assertFalse(J("espiao", d("2026-10-10T13:00:00"))[0])         # sábado
        self.assertTrue(J("interceptador", d("2026-10-09T02:00:00"))[0])   # 23h BRT
        self.assertFalse(N("interceptador", d("2026-10-08T21:00:00"))[0])  # 18h BRT: não voa
