"""03/10/2026: a rede aprende com a decisão humana MAIS RECENTE ("pendente" nunca bloqueia) e retreina quando os
rótulos crescem 5% — antes a validação automática (validacao_0000) bloqueava as 352 decisões humanas de 02/10."""
import gzip, json, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import rede_neural as RN


class TesteRotulos(unittest.TestCase):
    def test_decisao_mais_recente_vence_e_pendente_nao_bloqueia(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = Path(t) / "dados/oportunidades/validacao_mapa"; pasta.mkdir(parents=True)
            (pasta / "validacao_0000-automatica.json").write_text(json.dumps({"itens": [
                {"url": "https://a.gov.br/e1", "titulo": "E1", "decisao": "pendente"},
                {"url": "https://a.gov.br/e2", "titulo": "E2", "decisao": "valida_aberta"}]}), encoding="utf-8")
            (pasta / "validacao_2026-10-02c.json").write_text(json.dumps({"itens": [
                {"url": "https://a.gov.br/e1", "titulo": "E1", "decisao": "valida_aberta"},
                {"url": "https://a.gov.br/e2", "titulo": "E2", "decisao": "descartada", "motivo": "fora do objeto"}]}), encoding="utf-8")
            with mock.patch.object(RN, "ROOT", Path(t)):
                regs, y, pend = RN.dados_rotulados()
        r = {x["url"]: v for x, v in zip(regs, y)}
        self.assertEqual(r["https://a.gov.br/e1"], 1)          # a humana venceu a "pendente" automática
        self.assertEqual(r["https://a.gov.br/e2"], 0)          # a mais recente (descartada) venceu a mais antiga
        self.assertFalse(pend)

    def test_retreina_quando_os_rotulos_crescem(self):
        with tempfile.TemporaryDirectory() as t:
            arq = Path(t) / "modelo.json.gz"
            from datetime import date
            with gzip.open(arq, "wt", encoding="utf-8") as f:
                json.dump({"meta": {"treinada_em": date.today().isoformat(), "rotulados": 100}}, f)
            with mock.patch.object(RN, "MODELO", arq), mock.patch.object(RN, "dados_rotulados", return_value=([], [0] * 104, [])):
                self.assertFalse(RN.precisa_treinar())          # +4%: não
            with mock.patch.object(RN, "MODELO", arq), mock.patch.object(RN, "dados_rotulados", return_value=([], [0] * 106, [])):
                self.assertTrue(RN.precisa_treinar())           # +6%: sim


if __name__ == "__main__":
    unittest.main()
