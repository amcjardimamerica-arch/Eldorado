"""Teste de coleta e desempenho dos motores 01–21 (03/10/2026): ferramenta de dossiê e correções que ele apontou."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import sensores as S  # noqa: E402


class TestSensoresNaoQuebram(unittest.TestCase):
    def test_leitor_sem_lido_em_nao_derruba_o_passo(self):
        """19:10 de 02/10: KeyError 'lido_em' derrubou src.sensores e nenhuma leitura seguinte foi registrada."""
        tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, tmp, True)
        alvo = next(s for s in S.registro() if s["id"] == "dou")
        with mock.patch.object(S, "ESTADO", tmp / "esquadra.json"), mock.patch.object(S, "DB", tmp / "base.jsonl"), \
                mock.patch.object(S, "registro", return_value=[alvo]), \
                mock.patch.object(S, "registrar_dia", lambda *a, **k: None), \
                mock.patch.object(S, "ler", return_value={"achados": [], "falhas": []}), \
                mock.patch.dict(os.environ, {"MOTORES_FONTES": "dou", "MOTORES_BLOCO": "manual"}):
            r = S.run(hoje=date(2026, 10, 3), pausa=0)
        est = json.loads((tmp / "esquadra.json").read_text(encoding="utf-8"))
        self.assertIn("dou", est["sensores"])
        self.assertTrue(est["sensores"]["dou"]["ultima"], "a leitura fica registrada com a hora")
        self.assertEqual(est["ultima_execucao"]["sensores_executados"], 1)
        self.assertIsInstance(r, dict)


class TestAgenda(unittest.TestCase):
    def test_agenda_le_a_esquadra_e_trf1_volta_a_nuvem(self):
        src = (ROOT / "scripts/agenda_motores.py").read_text(encoding="utf-8")
        self.assertIn('"estado/esquadra.json"', src)
        self.assertNotIn('"estado/sensores.json"', src)
        ag = json.loads((ROOT / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        self.assertEqual(ag["dj-trf1-go"]["coleta"], "nuvem")
        sys.path.insert(0, str(ROOT / "scripts"))
        import agenda_motores as A
        # segunda, 07:53 BRT = 10:53 UTC: o motor 12 passa a ser disparado
        self.assertIn("dj-trf1-go", A.devidos(datetime(2026, 10, 5, 10, 53, tzinfo=timezone.utc)))


class TestFerramentaDeDossie(unittest.TestCase):
    def test_dossie_dos_21_motores(self):
        r = subprocess.run([sys.executable, "scripts/teste_motores.py", "1", "15"], cwd=ROOT, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        blocos = [json.loads(b) for b in r.stdout.replace("}\n{", "}\x00{").split("\x00")]
        self.assertEqual([b["id"] for b in blocos], ["do-goiania", "pncp-api"])
        for b in blocos:
            for chave in ("workflow", "onde_coleta", "resultado", "historico_3_anos"):
                self.assertIn(chave, b)
        self.assertGreater(blocos[1]["historico_3_anos"]["na_janela"], 0)

    def test_relatorios_dos_21_motores_existem(self):
        pasta = ROOT / "docs/relatorios/teste-motores-2026-10-03"
        pos = json.loads((ROOT / "config/ordem_motores.json").read_text(encoding="utf-8"))["posicoes"]
        for mid, n in pos.items():
            if int(n) <= 21:
                self.assertTrue((pasta / f"{int(n):02d}-{mid}.md").exists(), f"falta o relatório do motor {n}")
        self.assertTrue((pasta / "99-CONSOLIDADO.md").exists())


if __name__ == "__main__":
    unittest.main()
