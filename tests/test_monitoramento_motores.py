"""10/10 (titular): sinalizadores dos motores = monitoramento em três estados — funcionando (leu nas últimas 26 h),
falha (leitura com erro ou motor ativo há mais de 26 h sem ler), inativo (desativado, agregado ou nunca leu)."""
import sys, unittest
from datetime import datetime, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import status_motores as SM


class TesteTresEstados(unittest.TestCase):
    def setUp(self):
        self.ag, self.esq = SM._AGENDA, dict(SM._ESQ)
        SM._AGENDA = {"agregado": {"dias": "inativo", "agregado_a": "motor-x"}, "ativo": {"dias": "todos"}}; SM._ESQ.clear()

    def tearDown(self):
        SM._AGENDA = self.ag; SM._ESQ.clear(); SM._ESQ.update(self.esq)

    def _ult(self, horas):
        return datetime.now(SM.BRT) - timedelta(hours=horas)

    def test_funcionando_ontem_a_noite_nao_e_cinza(self):
        luz, txt, _ = SM.monitor({"id": "ativo"}, self._ult(14), "cinza", "", {})
        self.assertEqual(luz, "verde"); self.assertIn("funcionando", txt)

    def test_falha_por_atraso_e_por_erro(self):
        self.assertEqual(SM.monitor({"id": "ativo"}, self._ult(30), "cinza", "", {})[0], "vermelho")
        self.assertIn("não lê há", SM.monitor({"id": "ativo"}, self._ult(142), "cinza", "", {})[1])
        luz, txt, _ = SM.monitor({"id": "ativo"}, self._ult(0.5), "vermelho", "nenhuma página leu", {})
        self.assertEqual(luz, "vermelho"); self.assertIn("nenhuma página leu", txt)

    def test_inativo(self):
        self.assertEqual(SM.monitor({"id": "agregado"}, self._ult(1), "verde", "", {})[0], "cinza")
        self.assertEqual(SM.monitor({"id": "ativo"}, None, "cinza", "", {})[:2], ("cinza", "inativo — nunca leu"))

    def test_ultima_real_usa_a_esquadra(self):
        SM._ESQ["ativo"] = {"ultima": (datetime.now(SM.BRT) - timedelta(hours=1)).isoformat()}
        self.assertEqual(SM.monitor({"id": "ativo"}, self._ult(40), "cinza", "", {})[0], "verde", "a esquadra leu há 1 h")

    def test_painel_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('S.luz==="verde"?"Funcionando":S.luz==="vermelho"?"Falha":"Inativo"', h)
        self.assertIn("funcionando = leu nas últimas 26 h", h)
        w = (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        self.assertIn("leitura DIÁRIA dos sites (patrocínio privado e incentivos)", w)


if __name__ == "__main__":
    unittest.main()
