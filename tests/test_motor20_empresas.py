"""Teste do motor 20 (empresas da base ICMS/RFB/SALIC — incentivos fiscais) de 03/10/2026."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from src import empresas as E

ROOT = Path(__file__).resolve().parents[1]
PAGINA_ICMS = """<html><body><div class="entry-content">
<a href="https://goias.gov.br/economia/os-maiores-contribuintes-do-icms/">28 de janeiro de 2026</a>
<a href="https://goias.gov.br/economia/wp-content/uploads/sites/45/2026/01/MAIORES_DO_ICMS_OFICIAL_2025_CPF_Anon.pdf">Os maiores contribuintes de 2025</a>
<a href="https://goias.gov.br/economia/wp-content/uploads/sites/45/2026/01/MAIORES_DO_ICMS_OFICIAL_2024_CPF_Anon.pdf">Os maiores contribuintes de 2024</a>
</div></body></html>"""


class Motor20(unittest.TestCase):
    def test_nomes_que_nao_sao_empresa(self):
        for n in ("de janeiro de 2026", "WhatsApp Agenda Grupo", "Prefeitura de Aparecida e Instituto",
                  "REOLON ADVOGADOS ASSOCIADOS E DO INSTITUTO", "SOFTWARE S/A"):
            self.assertFalse(E.nome_valido(n), n)
        for n in ("LOJAS RENNER S A", "Diário de Goiás Comunicação LTDA", "VOTORANTIM CIMENTOS S A"):
            self.assertTrue(E.nome_valido(n), n)

    def test_limpeza_da_base_e_cnpj_verificado(self):
        base = {"a": {"nome": "de janeiro de 2026"}, "b": {"nome": "LOJAS RENNER S A"}, "c": {"nome": "Instituto Lojas Renner"},
                "d": {"nome": "Diário de Goiás Comunicação LTDA"}, "e": {"nome": "BRF S.A.", "cnpj": "01838723000127"}}
        r = E.limpar_base(base)
        self.assertNotIn("a", base)
        self.assertEqual(base["b"]["cnpj"], "92754738000162")                      # conferido em incentivos_verificados
        self.assertNotIn("cnpj", base["c"])                                        # instituto não herda o CNPJ da empresa
        self.assertEqual(r["descartadas_sem_cnpj"], ["de janeiro de 2026"])
        self.assertIn("Diário de Goiás Comunicação LTDA", r["pendentes_cnpj"])

    def test_lista_do_icms_ignora_o_link_da_data_e_le_os_pdfs_por_ano(self):
        lidos = []

        def get(url, timeout=25, binario=False):
            lidos.append(url)
            return b"PDF" if binario else PAGINA_ICMS
        with tempfile.TemporaryDirectory() as t, mock.patch.object(E, "PASTA", Path(t)), mock.patch.object(E, "_get", side_effect=get), \
                mock.patch.object(E, "_texto_pdf", return_value="x"), mock.patch.object(E.time, "sleep", lambda *_: None), \
                mock.patch.object(E, "extrair_contribuintes", side_effect=lambda txt, ano=None: [{"posicao": 1, "nome": f"EMPRESA {ano}", "cnpj": None}] if ano else []):
            (Path(t) / "go").mkdir()
            (Path(t) / "go/contribuintes_icms.json").write_text(json.dumps({"uf": "GO", "anos": {"2026": {"rotulo": "28 de janeiro de 2026", "empresas": [{"nome": "de janeiro de 2026"}]}}, "leituras": []}), encoding="utf-8")
            r = E.coletar_maiores_contribuintes("GO")
            salvo = json.loads((Path(t) / "go/contribuintes_icms.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(salvo["anos"]), ["2024", "2025"])                  # o falso "2026" saiu
        self.assertFalse([u for u in lidos[1:] if u.endswith("/os-maiores-contribuintes-do-icms/")])
        self.assertEqual(r["leitura"]["anexos_lidos"], 2)

    def test_semana_vencida_e_recuperada_pelo_fluxo_22(self):
        spec = importlib.util.spec_from_file_location("ed", ROOT / "scripts/empresas_devidas.py")
        ed = importlib.util.module_from_spec(spec); spec.loader.exec_module(ed)
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "s.jsonl"
            log.write_text(json.dumps({"em": "2026-09-20T10:50:39+00:00"}) + "\n", encoding="utf-8")
            with mock.patch.object(ed, "LOG", log):
                self.assertTrue(ed.devida(datetime(2026, 9, 28, 12, tzinfo=timezone.utc)))     # domingo 27/09 pulado
                self.assertFalse(ed.devida(datetime(2026, 9, 25, 12, tzinfo=timezone.utc)))
        wf = (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/empresas_devidas.py", wf)
        self.assertIn("python -m src.empresas semanal GO", wf)


if __name__ == "__main__":
    unittest.main()
