"""09/10 (titular): contagem semanal dos Pilotos zerada PELO PRÓPRIO PILOTO no início do voo — segunda 0h de Brasília
ou a pedido —, com os números antigos guardados; o carimbo viaja com os números, então um voo antigo que pousa depois
não ressuscita a contagem velha; o aprendizado a cada 100 buscas conta dentro da semana."""
import json
import lzma
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import reset_pilotos as R  # noqa: E402

U = lambda s: datetime.fromisoformat(s).astimezone(timezone.utc)  # noqa: E731


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._p = [mock.patch.object(R, "ROOT", self.tmp),
                   mock.patch.object(R, "PEDIDO", self.tmp / "estado/pilotos/zerar_contagem.json"),
                   mock.patch.object(R, "HIST_SEMANAL", self.tmp / "estado/pilotos/historico/contagem_semanal")]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def w(self, rel, d):
        p = self.tmp / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(d), encoding="utf-8")

    def r(self, rel):
        return json.loads((self.tmp / rel).read_text(encoding="utf-8"))

    def producao_antiga(self):
        self.w("estado/piloto/bordo.json", {"missao_atual": None, "missoes": [{"tipo": "descobrir", "inicio": "2026-10-07T10:00:00+00:00"}] * 60,
                                             "abates": {"piloto-aberto": {"n": 292, "ultimos": []}}, "total_abates": 295,
                                             "iniciado_em": "2026-09-22T10:34:19+00:00", "contagem_reiniciada_em": "2026-10-08T18:21:48+00:00"})
        self.w("estado/piloto/voos.json", {"2026-10-07": 73, "2026-10-08": 56, "2026-10-09": 37})
        self.w("estado/interceptador/bordo.json", {"abates": {"piloto-aberto": {"n": 2, "ouro": 2}}, "missoes": [{"em": "2026-10-09T10:00:00+00:00"}] * 60,
                                                    "total_abates": 55})
        self.w("docs/dados/interceptador.json", {"papel": "Piloto - Interceptador", "fila": {"x": 3},
                                                  "acumulado": {"missoes": 722, "validadas": 38, "serve_como_fonte": {"sim": 1}, "tempo_medio_min": 2.5},
                                                  "missoes": [{"em": "2026-10-09"}] * 40})


class TesteSemana(_Base):
    def test_segunda_zero_hora_de_brasilia(self):
        self.assertEqual(R.inicio_semana(U("2026-10-11T23:59:00-03:00")), U("2026-10-05T00:00:00-03:00"))
        self.assertEqual(R.inicio_semana(U("2026-10-12T00:00:00-03:00")), U("2026-10-12T00:00:00-03:00"))
        self.assertEqual(R.inicio_semana(U("2026-10-12T02:30:00+00:00")), U("2026-10-05T03:00:00+00:00"), "domingo 23h30 em Brasília")

    def test_pedido_vale_so_a_partir_da_hora_e_so_dentro_da_semana(self):
        R.pedir("teste", agora=U("2026-10-08T18:21:48+00:00"))
        self.assertEqual(R.inicio_contagem(U("2026-10-09T12:00:00+00:00")), "2026-10-08T18:21:48+00:00")
        self.assertEqual(R.inicio_contagem(U("2026-10-08T18:00:00+00:00")), "2026-10-05T03:00:00+00:00", "pedido futuro não vale ainda")
        self.assertEqual(R.inicio_contagem(U("2026-10-12T03:00:00+00:00")), "2026-10-12T03:00:00+00:00", "a segunda seguinte passa à frente")


class TesteZeramento(_Base):
    def test_zera_guarda_e_e_idempotente(self):
        self.producao_antiga()
        agora = U("2026-10-09T15:00:00+00:00")
        for piloto in ("espiao", "interceptador"):
            r = R.zerar_se_preciso(piloto, agora=agora)
            self.assertTrue(r["zerou"]); self.assertTrue((self.tmp / r["numeros_antigos_em"]).exists())
            self.assertFalse(R.zerar_se_preciso(piloto, agora=agora)["zerou"], "segundo voo da mesma semana não zera")
        b = self.r("estado/piloto/bordo.json")
        self.assertEqual((b["missoes"], b["abates"], b["total_abates"]), ([], {}, 0))
        self.assertNotIn("contagem_reiniciada_em", b); self.assertEqual(b["contagem"]["desde"], "2026-10-05T03:00:00+00:00")
        self.assertEqual(self.r("estado/piloto/voos.json"), {"_contagem": b["contagem"]})
        bi = self.r("estado/interceptador/bordo.json"); self.assertEqual((bi["missoes"], bi["abates"], bi["total_abates"]), ([], {}, 0))
        pub = self.r("docs/dados/interceptador.json")
        self.assertEqual(pub["acumulado"]["missoes"], 0); self.assertEqual(pub["missoes"], []); self.assertEqual(pub["fila"], {"x": 3})
        # os números antigos estão inteiros no histórico
        arqs = sorted(R.HIST_SEMANAL.glob("espiao_*.json.xz"))
        h = json.loads(lzma.decompress(arqs[0].read_bytes()))
        self.assertEqual(h["arquivos"]["estado/piloto/bordo.json"]["total_abates"], 295)
        self.assertEqual(h["resumo"]["estado/piloto/voos.json"], {"voos": 166, "dias": 3})

    def test_voo_antigo_que_pousa_depois_nao_ressuscita_a_contagem(self):
        """O defeito de 08/10: o voo decolado antes do reset gravou os números velhos por cima."""
        self.producao_antiga()
        R.zerar_se_preciso("espiao", agora=U("2026-10-09T15:00:00+00:00"))
        self.producao_antiga()                                      # o pouso do voo antigo (código velho, sem carimbo)
        r = R.zerar_se_preciso("espiao", agora=U("2026-10-09T15:05:00+00:00"))
        self.assertTrue(r["zerou"]); self.assertEqual(self.r("estado/piloto/bordo.json")["total_abates"], 0)
        self.assertEqual(len(list(R.HIST_SEMANAL.glob("espiao_*"))), 2, "o pouso tardio também fica guardado")

    def test_segunda_feira_e_pedido(self):
        self.producao_antiga()
        R.zerar_se_preciso("espiao", agora=U("2026-10-09T15:00:00+00:00"))
        b = self.r("estado/piloto/bordo.json"); b["missoes"] = [{"tipo": "x"}]; b["total_abates"] = 4
        self.w("estado/piloto/bordo.json", b)
        self.assertFalse(R.zerar_se_preciso("espiao", agora=U("2026-10-12T02:59:00+00:00"))["zerou"], "domingo 23h59 ainda é a mesma semana")
        r = R.zerar_se_preciso("espiao", agora=U("2026-10-12T03:00:00+00:00"))
        self.assertTrue(r["zerou"]); self.assertEqual(r["motivo"], "segunda-feira 0h (Brasília)")
        self.w("estado/piloto/bordo.json", {**self.r("estado/piloto/bordo.json"), "total_abates": 9})
        R.pedir("titular", agora=U("2026-10-13T12:00:00+00:00"))
        r = R.zerar_se_preciso("espiao", agora=U("2026-10-13T12:01:00+00:00"))
        self.assertTrue(r["zerou"]); self.assertEqual(r["motivo"], "pedido da titular")
        self.assertEqual(self.r("estado/piloto/bordo.json")["contagem"]["desde"], "2026-10-13T12:00:00+00:00")

    def test_contar_voo_preserva_o_carimbo(self):
        from src import piloto as P
        R.zerar_se_preciso("espiao", agora=U("2026-10-09T15:00:00+00:00"))
        with mock.patch.object(P, "PASTA", self.tmp / "estado/piloto"):
            self.assertEqual(P._contar_voo(), 1); self.assertEqual(P._contar_voo(), 2)
        v = self.r("estado/piloto/voos.json")
        self.assertIn("_contagem", v); self.assertEqual(sum(x for k, x in v.items() if not k.startswith("_")), 2)


class TesteAprendizadoNaSemana(_Base):
    def test_cem_buscas_contadas_dentro_da_semana(self):
        from src.skills import aprendizado as A
        rel = [{"em": "2026-10-01T10:00:00+00:00", "qualidade": "insuficiente"}] * 150 + [{"em": "2026-10-06T10:00:00+00:00", "qualidade": "parcial"}] * 30
        self.w("estado/interceptador/relatorios/2026-10-06.json", {"voos": rel})
        par = {"interceptador": {"estrategia_criativa": {"id": "I007", "pesquisas_no_inicio": 150, "rotas": ["a"]}, "estrategias_anteriores": []},
               "espiao": {"estrategia_criativa": {"id": "E001", "pool": ["q"] * 9, "pesquisas_no_inicio": 0}, "estrategias_anteriores": []}}
        self.w("config/parametros_pilotos.json", par)
        with mock.patch.object(A, "ROOT", self.tmp), mock.patch.object(A, "PAR", self.tmp / "config/parametros_pilotos.json"), \
                mock.patch.object(A, "PAR_FIXOS", self.tmp / "config/parametros_pilotos_fixos.json"), \
                mock.patch.object(R, "inicio_contagem", lambda agora=None: "2026-10-05T03:00:00+00:00"):
            A.ciclo_criativo()
            pi = A.parametros()["interceptador"]
            self.assertEqual(pi["estrategia_criativa"]["id"], "I007", "30 estudos na semana: ainda não troca")
            self.assertEqual(pi["estrategia_criativa"]["pesquisas_no_inicio"], 0)
            self.assertEqual(pi["estrategia_criativa"]["contagem_desde"], "2026-10-05T03:00:00+00:00")
            self.w("estado/interceptador/relatorios/2026-10-07.json", {"voos": [{"em": "2026-10-07T10:00:00+00:00", "qualidade": "validada"}] * 70})
            A.ciclo_criativo()
            pi = A.parametros()["interceptador"]
            self.assertEqual(pi["estrategia_criativa"]["id"], "I002", "100 estudos dentro da semana: estratégia nova")
            self.assertEqual(pi["estrategias_anteriores"][-1]["estudos"], 100)


class TesteProducaoReal(_Base):
    def test_numeros_reais_de_hoje_vao_inteiros_para_o_historico(self):
        """Cópia dos arquivos reais (sem tocar nos originais): tudo o que está lá vai para o histórico."""
        for piloto, arqs in R.ARQUIVOS.items():
            for a in arqs:
                if (ROOT / a).exists():
                    (self.tmp / a).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / a, self.tmp / a)
        antes = {a: (ROOT / a).read_bytes() for arqs in R.ARQUIVOS.values() for a in arqs if (ROOT / a).exists()}
        for piloto in R.ARQUIVOS:
            r = R.zerar_se_preciso(piloto)
            self.assertTrue(r["zerou"])
            h = json.loads(lzma.decompress((self.tmp / r["numeros_antigos_em"]).read_bytes()))
            for a in R.ARQUIVOS[piloto]:
                if a in antes:
                    self.assertEqual(h["arquivos"][a], json.loads(antes[a]))
        self.assertEqual(antes, {a: (ROOT / a).read_bytes() for a in antes}, "os arquivos de produção não foram tocados")


if __name__ == "__main__":
    unittest.main()
