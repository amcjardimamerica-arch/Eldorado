"""14/10/2026 (titular): só Goiás tem municipais — e as CAPITAIS dos outros estados; o motor que encontra a municipal
de outro estado (fora das capitais) a descarta na coleta."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import regra_abrangencia as A


class TesteRegra(unittest.TestCase):
    def setUp(self):
        self._r = A.REGISTRO; A.REGISTRO = Path(tempfile.mkdtemp()) / "d.json"

    def tearDown(self):
        A.REGISTRO = self._r

    def test_capitais_ficam_demais_saem(self):
        D = A.descartar_na_coleta
        self.assertIsNone(D({"titulo": "Chamamento — Prefeitura Municipal de Curitiba", "orgao": "Prefeitura de Curitiba", "uf": "PR"}))
        self.assertIsNone(D({"titulo": "Edital", "orgao": "Prefeitura de São Paulo", "uf": "SP"}))
        self.assertTrue(D({"titulo": "Edital — Prefeitura de Campinas", "orgao": "Prefeitura de Campinas", "uf": "SP"}))
        self.assertTrue(D({"titulo": "MUNICIPIO DE ITAGIBA — Chamamento", "uf": "BA"}))
        self.assertIsNone(D({"titulo": "Credenciamento", "orgao": "MUNICIPIO DE SENADOR CANEDO"}))
        self.assertIsNone(D({"titulo": "Edital estadual", "orgao": "Secretaria de Estado", "nivel": "estadual", "uf": "MG"}))
        self.assertIsNone(A.capital_citada("campanha de natal de luz"))
        self.assertEqual(A.capital_citada("Prefeitura de Belo Horizonte/MG"), "MG")

    def test_motor_descarta_na_coleta_e_registra(self):
        from src.nucleo import merge_registro
        r = merge_registro(None, {"id": "x", "titulo": "Edital — Prefeitura de Campinas", "orgao": "Prefeitura de Campinas", "uf": "SP", "fonte_id": "pncp-api"})
        self.assertTrue(r.get("_descartado_na_coleta"))
        self.assertEqual(json.loads(A.REGISTRO.read_text())["por_motor"]["pncp-api"]["total"], 1)
        for f, marca in (("src/sensores.py", "_abr(s.get(\"id\"), a)"), ("src/indexadores/motor.py", "_abr(it.get(\"fonte\") or \"indexador\", it, it.get(\"uf\"))"),
                         ("src/espiao_foco.py", "_abr(\"piloto-espiao\""), ("src/nucleo.py", "if not x.get(\"_descartado_na_coleta\")")):
            self.assertIn(marca, (ROOT / f).read_text(encoding="utf-8"), f)

    def test_livro_de_capital_fica(self):
        from src.curadoria_biblioteca import fora_da_abrangencia
        self.assertFalse(fora_da_abrangencia({"id": "l", "programa": "Edital da Prefeitura de Recife", "orgao": "Prefeitura do Recife", "geo": "PE", "pagina": "https://www2.recife.pe.gov.br/edital"}))


if __name__ == "__main__":
    unittest.main()


class TesteSalaTempoReal(unittest.TestCase):
    """14/10/2026 (titular): sala de controle em tempo real."""
    def test_fluxo_37_e_recarga_por_minuto(self):
        w = (ROOT / ".github/workflows/sala-tempo-real.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_run:", w); self.assertIn('cron: "*/10 * * * *"', w); self.assertIn("cancel-in-progress: true", w)
        for m in ("src.sala_controle", "src.status_motores", "src.diagnostico_sistema", "R.construir(gravar=True)"):
            self.assertIn(m, w)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("},60000);", h); self.assertIn('style.display==="block") return;', h)

    def test_datas_dos_indicadores(self):
        from datetime import datetime, timezone
        from src import sala_controle as S
        self.assertIsNotNone(S._horas("2026-10-14", datetime(2026, 10, 15, tzinfo=timezone.utc)))
        self.assertIn('quando=mon.get("em") or op.get("atualizado_em")', (ROOT / "src/sala_controle.py").read_text(encoding="utf-8"))
