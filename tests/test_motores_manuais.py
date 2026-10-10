"""10/10 (titular): o FOGO desliga/religa um motor à mão. Desligado, nenhum acionamento automático o executa (escala,
maestro, rede neural, voos, empresas) até religar; com fogo, volta ao workflow."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import motores_manuais as M


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.o = (M.CONFIG, M.PUBLICO, dict(M.PAUSA_PILOTOS))
        M.CONFIG = T / "c.json"; M.PUBLICO = T / "p.json"
        M.PAUSA_PILOTOS.update({"piloto-aberto": T / "piloto_pausado", "piloto-espiao": T / "piloto_pausado", "piloto-interceptador": T / "int/pausado"})

    def tearDown(self):
        M.CONFIG, M.PUBLICO = self.o[0], self.o[1]; M.PAUSA_PILOTOS.clear(); M.PAUSA_PILOTOS.update(self.o[2]); self.tmp.cleanup()


class TesteRegra(Base):
    def test_desligar_e_religar(self):
        M.definir("plat-salic", "desligado")
        self.assertTrue(M.desligado("plat-salic")); self.assertTrue(M.desligado("salic"), "aceita o id com e sem plat-")
        self.assertIn("plat-salic", json.loads(M.PUBLICO.read_text())["desligados"])
        M.definir("salic", "ligado")
        self.assertFalse(M.desligado("plat-salic"))
        self.assertEqual([h["estado"] for h in M.carregar()["historico"]], ["desligado", "ligado"])

    def test_pilotos_usam_a_pausa_que_os_fluxos_respeitam(self):
        M.definir("piloto-interceptador", "desligado")
        self.assertTrue(M.PAUSA_PILOTOS["piloto-interceptador"].exists())
        M.definir("piloto-interceptador", "ligado")
        self.assertFalse(M.PAUSA_PILOTOS["piloto-interceptador"].exists())

    def test_escala_nao_aciona_o_desligado(self):
        from src import sensores as S
        base = S.escala_do_dia(date(2026, 10, 12))
        alvo = base["saem"][0]["id"] if base["saem"] else None
        if not alvo:
            self.skipTest("escala vazia nesta data")
        M.definir(alvo, "desligado")
        e = S.escala_do_dia(date(2026, 10, 12))
        self.assertNotIn(alvo, [x["id"] for x in e["saem"]]); self.assertIn(alvo, e["desligados_no_fogo"])
        M.definir(alvo, "ligado")
        self.assertIn(alvo, [x["id"] for x in S.escala_do_dia(date(2026, 10, 12))["saem"]], "com fogo, volta ao workflow")

    def test_espiao_patrocinio_e_incentivos_respeitam(self):
        from src import piloto, patrocinios, biblioteca_empresas
        for mid in ("piloto-aberto", "motor-patrocinio", "motor-gife"):
            M.definir(mid, "desligado")
        self.assertTrue(piloto.ciclo().get("desligado_no_fogo"))
        self.assertTrue(patrocinios.run().get("desligado_no_fogo"))
        self.assertTrue(biblioteca_empresas.run().get("desligado_no_fogo"))

    def test_monitoramento_mostra_desligado(self):
        from src import status_motores as SM
        M.definir("dou", "desligado")
        luz, txt, _ = SM.monitor({"id": "dou"}, None, "verde", "", {})
        self.assertEqual(luz, "cinza"); self.assertIn("desligado por você no fogo", txt)


class TestePainelEFluxo(unittest.TestCase):
    def test_painel_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('ghDispatch("motor-manual.yml"', h); self.assertIn("function fogoDoRepositorio", h)
        w = (ROOT / ".github/workflows/motor-manual.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.motores_manuais definir", w); self.assertIn("options: [desligado, ligado]", w)


if __name__ == "__main__":
    unittest.main()
