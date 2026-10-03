"""Testes das correções de 03/10/2026: ponte Hostgator, histórico de 3 anos, Rouanet/SALIC, motor 19, fluxo 22."""
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]


class PonteBrasil(unittest.TestCase):
    def test_so_passa_pela_ponte_na_nuvem_configurada_e_dominio_brasileiro(self):
        from src import ponte_brasil as P
        self.assertTrue(P.precisa("https://suap.goiania.go.leg.br/x"))
        self.assertTrue(P.precisa("https://www.tjgo.jus.br/index.php/x"))
        self.assertTrue(P.precisa("https://www.anapolis.go.gov.br/"))
        self.assertFalse(P.precisa("https://www.in.gov.br/leiturajornal"))
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False), \
                mock.patch.object(P, "configurada", return_value=True):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            self.assertTrue(P.usar("https://www.tjgo.jus.br/"))
            self.assertFalse(P.usar("https://www.in.gov.br/"))
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}), mock.patch.object(P, "configurada", return_value=False):
            self.assertFalse(P.usar("https://www.tjgo.jus.br/"))
            self.assertFalse(P.disponivel())
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(P.usar("https://www.tjgo.jus.br/"))      # no computador do titular a leitura é direta
            self.assertTrue(P.disponivel())


class Historico3Anos(unittest.TestCase):
    def test_situacao_e_arquivo_sem_repetir(self):
        from src import historico_3_anos as H
        hoje = date(2026, 10, 3)
        self.assertEqual(H.situacao({"fim": "2025-05-01"}, hoje), "encerrada")
        self.assertEqual(H.situacao({"fim": "2026-11-01"}, hoje), "aberta")
        self.assertEqual(H.situacao({"data_publicacao": "2026-09-30"}, hoje), "sem_prazo")
        self.assertEqual(H.inicio(hoje), date(2023, 10, 3))
        with tempfile.TemporaryDirectory() as t, mock.patch.object(H, "ARQ", Path(t)):
            regs = [{"id": "a", "titulo": "Edital 1", "data_publicacao": "2024-03-01", "fim": "2024-04-01"},
                    {"id": "b", "titulo": "Edital 2", "data_publicacao": "2026-09-01", "fim": "2026-12-01"}]
            self.assertEqual(H.arquivar("dou", regs, hoje), 2)
            self.assertEqual(H.arquivar("dou", regs, hoje), 0)
            linha = json.loads((Path(t) / "dou/2024.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(linha["situacao"], "encerrada")      # encerrada = arquivo para a previsão

    def test_rodar_retoma_pelo_cursor_e_gera_livros(self):
        from src import historico_3_anos as H
        hoje = date(2026, 10, 3)
        lidos = []
        fake = {"periodos": lambda h: ["p1", "p2", "p3"],
                "ler": lambda p, ctx: (lidos.append(p) or [{"id": p, "titulo": p, "data_publicacao": "2025-01-0" + p[-1]}])}
        with tempfile.TemporaryDirectory() as t, mock.patch.dict(H.MOTORES, {"dou": fake}), \
                mock.patch.object(H, "ARQ", Path(t) / "a"), mock.patch.object(H, "EST", Path(t) / "e"), \
                mock.patch.object(H, "RESUMO", Path(t) / "r.json"), \
                mock.patch.object(H, "livros", return_value={"livros_novos": 3}) as liv:
            r = H.rodar("dou", minutos=5, hoje=hoje)
            self.assertTrue(r["concluido"])
            self.assertEqual(r["oportunidades"], 3)
            liv.assert_called_once()
            r2 = H.rodar("dou", minutos=5, hoje=hoje)
            self.assertEqual(r2["periodos_lidos"], 0)                # o cursor não relê o que já foi feito
            self.assertEqual(lidos, ["p1", "p2", "p3"])


class RouanetSalic(unittest.TestCase):
    def test_janela_da_in_29_2026(self):
        from src import rouanet_salic as R
        self.assertTrue(R.janela(date(2026, 10, 3))["aberta"])
        self.assertEqual(R.janela(date(2026, 10, 3))["dias_restantes"], 28)
        self.assertFalse(R.janela(date(2026, 11, 2))["aberta"])
        self.assertEqual(R.janela(date(2026, 11, 2))["inicio"], "2027-02-01")
        self.assertFalse(R.janela(date(2026, 1, 15))["aberta"])
        reg = R.registro_janela(date(2026, 10, 3))
        self.assertEqual(reg["fim"], "2026-10-31")
        self.assertIn("art. 5º", reg["evidencia"])

    def test_pessoa_fisica_nunca_entra(self):
        from src import rouanet_salic as R
        self.assertIsNone(R._limpo({"PRONAC": 1, "cgccpf": "123.456.789-01", "proponente": "Fulano"}))
        r = R._limpo({"PRONAC": 2, "cgccpf": "12.345.678/0001-90", "proponente": "Associação X"})
        self.assertEqual(r["cgccpf"], "12345678000190")
        self.assertEqual(r["id"], "salic-2")


class Motor19(unittest.TestCase):
    def test_banco_de_empresas_destinadoras(self):
        d = json.loads((RAIZ / "config/empresas_destinadoras.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(d["com_braco_social"], 25)
        renner = [e for e in d["empresas"] if e["cnpj"] == "92754738000162"][0]
        self.assertIn("Rouanet", renner["mecanismos_confirmados"])
        self.assertEqual(renner["bracos_sociais"][0]["nome"], "Instituto Lojas Renner")
        for e in d["empresas"]:
            for b in e["bracos_sociais"]:
                self.assertTrue(b["gife"].startswith("https://gife.org.br/associados/"))
                self.assertIn(b["vinculo"], ("confirmado", "a_confirmar"))
            if not e["bracos_sociais"] and e["destina"]:
                self.assertIn("não verificado", e["instituto"])        # nunca "não tem"

    def test_rotas_sem_dominio_adivinhado(self):
        from src.empresas_rotas import rotas_para_sensor
        r = rotas_para_sensor(40)
        self.assertIn("https://www.institutolojasrenner.org.br/", r)
        self.assertFalse([u for u in r if "duckduckgo" in u])
        self.assertEqual(len(r), len(set(r)))


class Fluxo22EStatus(unittest.TestCase):
    def test_workflows_sem_env_vazio(self):
        for p in (RAIZ / ".github/workflows").glob("*.yml"):
            linhas = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
            for i, l in enumerate(linhas):
                if l.strip() == "env:":
                    rec = len(l) - len(l.lstrip())
                    prox = linhas[i + 1] if i + 1 < len(linhas) else ""
                    self.assertGreater(len(prox) - len(prox.lstrip()), rec, f"env vazio em {p.name}")

    def test_fluxo_22_calcula_a_propria_lista(self):
        txt = (RAIZ / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/motores_da_vez.py", txt)
        self.assertIn("eldorado-varredura-diaria", txt)
        self.assertIn("ELDORADO_PONTE_URL", txt)

    def test_motores_da_vez_ordem_do_painel(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("mdv", RAIZ / "scripts/motores_da_vez.py")
        M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(M)
        with mock.patch("src.maestro.controlar", return_value={"a_disparar": ["plat-gife", "dou", "motor-gife"]}):
            ids = M.lista(disparar=False)
        self.assertNotIn("motor-gife", ids)
        if "dou" in ids and "plat-gife" in ids:
            self.assertLess(ids.index("dou"), ids.index("plat-gife"))

    def test_status_traz_leitura_do_dia(self):
        d = json.loads((RAIZ / "docs/dados/status_motores.json").read_text(encoding="utf-8"))
        ms = d.get("motores") or []
        self.assertTrue(ms)
        for m in ms:
            self.assertIn(m["leitura_do_dia"]["estado"], ("completa", "parcial", "pendente", "fora_da_agenda", "regra_fixa"))


if __name__ == "__main__":
    unittest.main()
