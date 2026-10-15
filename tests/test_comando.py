"""15/10/2026 (titular): a rede neural e o maestro são o mesmo comando — decide, aciona, avalia, reaciona, direciona."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import comando as C


class Comando(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = [mock.patch.object(C, n, self.d / f) for n, f in (("DIR", "c"), ("CICLO", "c/ciclo.json"), ("PAINEL", "painel.json"), ("PARA_CHROME", "c/chrome.json"))]
        for x in self.p:
            x.start()
        self.addCleanup(lambda: [x.stop() for x in self.p])

    def test_recibo_detecta_erro_mesmo_com_codigo_zero(self):
        r = C.executar("x", [sys.executable, "-c", "print('Traceback (most recent call last):'); print('TypeError: boom')"], 30)
        self.assertEqual(r["rc"], 0)
        self.assertIn("TypeError", r["erro"])
        self.assertIsNone(C.executar("ok", [sys.executable, "-c", "print('tudo certo')"], 30)["erro"])

    def test_reaciona_na_mesma_passagem_e_manda_o_local_ao_humano(self):
        chamadas = []
        avals = iter([{"cobertura_do_dia_pct": 40, "estado": {"a": "parcial", "b": "pendente_local", "c": "completa"}, "reacionar": ["a"],
                       "para_humano": ["b"], "completos": 1},
                      {"cobertura_do_dia_pct": 80, "estado": {"a": "completa", "b": "pendente_local", "c": "completa"}, "reacionar": [],
                       "para_humano": ["b"], "completos": 2}])
        with mock.patch.object(C, "decidir_coleta", lambda: {"motores": ["a", "b", "c"], "adiados": [], "valor": {}}), \
             mock.patch.object(C, "acionar", lambda ms, prazo: chamadas.append(list(ms)) or {"etapa": "acionar", "erro": None, "novos_na_base": 2}), \
             mock.patch.object(C, "avaliar_coleta", lambda ms: next(avals)):
            c = C.ciclo_coleta()
        self.assertEqual(chamadas, [["a", "b", "c"], ["a"]])
        self.assertEqual(c["avaliacao"]["completos"], 2)
        self.assertIn("b", json.loads((self.d / "c/chrome.json").read_text())["itens"])

    def test_sequencia_com_portao_e_veredito_vermelho(self):
        (self.d / "c").mkdir(exist_ok=True)
        (self.d / "c/ciclo.json").write_text(json.dumps({"recibos": [], "decisoes": [], "novos_na_base": 0}))
        fs = [{"etapa": "pula", "finalidade": "f", "cmds": [[sys.executable, "-c", "1"]], "t": 30, "pular": "nada novo"},
              {"etapa": "ok", "finalidade": "f", "cmds": [[sys.executable, "-c", "print(1)"]], "t": 30, "pular": None},
              {"etapa": "quebra", "finalidade": "f", "cmds": [[sys.executable, "-c", "raise ValueError('x')"]], "t": 30, "pular": None}]
        with mock.patch.object(C, "fases", lambda ctx: fs), mock.patch.object(C, "_hoje_brt", lambda: "2026-10-15"):
            ctx = C.ciclo_sequencia()
            self.assertEqual(ctx["estado"], "vermelho")
            self.assertEqual([d["fase"] for d in ctx["decisoes"]], ["pula"])
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):          # não vira anotação falsa no GitHub
                self.assertEqual(C.veredito(), 1)
        self.assertEqual(json.loads((self.d / "painel.json").read_text())["vermelhos_hoje"], 1)


if __name__ == "__main__":
    unittest.main()


class SemAgenda(unittest.TestCase):
    """15/10/2026 (titular): a agenda foi incorporada — todo motor ativo é lido todo dia."""
    def test_plano_do_dia_tem_todos_os_motores_ativos(self):
        from src import maestro as M
        from src import sensores as S
        ativos = {s["id"] for s in S.registro()}
        plano = {p["motor"] for p in M.planejar()}
        self.assertEqual(plano, ativos)

    def test_sem_estado_de_horario(self):
        import inspect
        from src import maestro as M
        self.assertNotIn("aguardando_horario", inspect.getsource(M.controlar))
        self.assertNotIn("roda_hoje(ag", inspect.getsource(M.planejar))


class Ciclo6_15_10(unittest.TestCase):
    def test_cartorio_40_por_passagem_e_unico_gravador(self):
        import yaml
        from pathlib import Path
        src = (Path(__file__).resolve().parents[1] / "src/comando.py").read_text(encoding="utf-8")
        self.assertIn('"src.cartorio", "--limite", "40"', src)
        y = yaml.safe_load((Path(__file__).resolve().parents[1] / ".github/workflows/cartorio.yml").read_text(encoding="utf-8"))
        self.assertEqual(list(y[True].keys()), ["workflow_dispatch"])          # só manual: o comando é o único gravador

    def test_status_semanal_e_api_com_achados(self):
        from src import status_motores as SM
        self.assertGreater(SM.janela_do_motor({"id": "motor-gife"}, {"dias": "todos"}), 7 * 24)
