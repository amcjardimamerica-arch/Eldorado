"""Correções apontadas pelo conselho em 23/09, depois de 24 h de voo."""
import json, os, pathlib, tempfile, unittest
from src.aprendizados_piloto import _e_ensaio, avaliar, ENSAIO
from src.briefing_piloto import escrever, _registrar_mudez
ROOT = pathlib.Path(__file__).resolve().parents[1]

def setUpModule():
    """A base de aprendizados vai para uma pasta temporária: teste não escreve em produção."""
    global _TMP
    _TMP = tempfile.mkdtemp(prefix="aprendizados-")
    os.environ["ELDORADO_APRENDIZADOS"] = _TMP
    import importlib, src.aprendizados_piloto as A
    importlib.reload(A)


def tearDownModule():
    import importlib, shutil, src.aprendizados_piloto as A
    os.environ.pop("ELDORADO_APRENDIZADOS", None)
    importlib.reload(A)
    shutil.rmtree(_TMP, ignore_errors=True)



class _Mudo:
    def perguntar(self, p, e=None): return None


class TesteEnsaioNaoContaminaABase(unittest.TestCase):
    """23/09: as estatísticas apareceram com 26 missões de motores que não existem —
    m-teste, m-seco, m-repete. Eram os testes escrevendo na base de produção."""

    def test_reconhece_motor_de_ensaio(self):
        for m in ("m-teste", "m-seco", "m-repete", "lab-motor", "ensaio-motor", "teste"):
            self.assertTrue(_e_ensaio(m), m)
        for m in ("motor-gife", "pncp-api", "empresas-incentivadas", "missao-especial"):
            self.assertFalse(_e_ensaio(m), m)

    def test_missao_de_ensaio_nao_e_gravada(self):
        r = avaliar(_Mudo(), {"motor": "m-teste", "tipo": "cacar_oportunidade", "licao": "x"}, [])
        self.assertTrue(r["avaliacao"]["ensaio"])
        self.assertIn("não gravada", r["avaliacao"]["nota"])

    def test_a_base_publicada_nao_tem_ensaio(self):
        d = json.loads((ROOT / "docs/dados/aprendizados_piloto.json").read_text(encoding="utf-8"))
        for motor in (d.get("por_motor") or {}):
            self.assertFalse(_e_ensaio(motor), motor)
        for l in (d.get("licoes") or []):
            self.assertFalse(_e_ensaio(l.get("motor")), l.get("motor"))


class TesteResgatePeloSiteDoOrgao(unittest.TestCase):
    """30 de 32 resgates falharam procurando a página no buscador. O chamamento de um
    município está no portal dele, não no índice de um buscador."""

    def test_le_o_site_do_orgao_antes_de_buscar(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("PRIMEIRO O SITE DO ÓRGÃO", src)
        self.assertIn("buscar_na_fonte", src)
        self.assertIn("if not dados else []", src)        # buscador vira segunda via
        self.assertLess(src.index("PRIMEIRO O SITE DO ÓRGÃO"),
                        src.index("o buscador vira segunda via"))
        self.assertIn('"via": "site do órgão"', src)      # a lição registra por onde veio


class TesteRedeDeSegurancaComRumo(unittest.TestCase):
    """Em 12 voos houve 2 apostas distintas: a rede devolvia sempre a mesma pergunta."""

    def test_rumo_sorteado_do_catalogo_sem_repetir(self):
        rumos = [escrever(_Mudo())["aposta"]["onde"] for _ in range(6)]
        self.assertGreaterEqual(len(set(rumos)), 5, f"rumos repetidos: {rumos}")
        self.assertNotIn("livre", rumos)

    def test_carimbo_ao_milissegundo(self):
        src = (ROOT / "src/briefing_piloto.py").read_text(encoding="utf-8")
        self.assertIn("%H%M%S-%f", src)
        self.assertIn("colidiam no mesmo", src)

    def test_marca_o_voo_como_modelo_mudo(self):
        b = escrever(_Mudo())
        self.assertTrue(b.get("modelo_mudo"))
        self.assertEqual(b["aposta"]["confianca"], "baixa")
        self.assertIn("sorteado do catálogo", b["aposta"]["porque"])


class TesteMudezMedidaNoCargo(unittest.TestCase):
    def setUp(self):
        import os; os.environ["ELDORADO_VOO_REAL"] = "1"      # simulam um voo real, só aqui

    def tearDown(self):
        import os; os.environ.pop("ELDORADO_VOO_REAL", None)

    def test_fora_do_voo_real_nada_e_contado(self):
        import os; os.environ.pop("ELDORADO_VOO_REAL", None)
        arq = ROOT / "estado/piloto/desempenho_em_voo.json"
        antes = arq.read_text(encoding="utf-8") if arq.exists() else None
        _registrar_mudez(True)
        depois = arq.read_text(encoding="utf-8") if arq.exists() else None
        self.assertEqual(antes, depois)

    """O cargo exige ≥50% de acerto. Um modelo que não responde entrega zero, e isso
    precisa estar medido no arquivo do cargo para a substituição poder ser decidida."""

    def test_conta_pedidos_e_mudos(self):
        """O contador mora em estado/ desde 24/09: o voo não commita o arquivo do cargo, e ali
        ele sumia a cada pouso (0 pedidos depois de dois voos do Qwen3)."""
        from src.cargo_piloto import ocupante
        arq = ROOT / "estado/piloto/desempenho_em_voo.json"
        antes = arq.read_text(encoding="utf-8") if arq.exists() else None
        oid = (ocupante() or {}).get("id") or "vago"
        try:
            arq.write_text("{}", encoding="utf-8")
            for _ in range(10):
                _registrar_mudez(True)
            d = json.loads(arq.read_text(encoding="utf-8"))[oid]
            self.assertEqual(d["pedidos"], 10); self.assertEqual(d["mudos"], 10)
            self.assertEqual(d["taxa_de_resposta"], 0.0)
            self.assertIn("abaixo dos 50%", d["alerta"])
            self.assertIn("banco de reserva", d["alerta"])
            _registrar_mudez(False)
            d = json.loads(arq.read_text(encoding="utf-8"))[oid]
            self.assertGreater(d["taxa_de_resposta"], 0)
        finally:
            arq.unlink(missing_ok=True)
            if antes is not None:
                arq.write_text(antes, encoding="utf-8")

    def test_sem_alerta_enquanto_a_amostra_e_pequena(self):
        from src.cargo_piloto import ocupante
        arq = ROOT / "estado/piloto/desempenho_em_voo.json"
        antes = arq.read_text(encoding="utf-8") if arq.exists() else None
        oid = (ocupante() or {}).get("id") or "vago"
        try:
            arq.write_text("{}", encoding="utf-8")
            for _ in range(3):
                _registrar_mudez(True)
            d = json.loads(arq.read_text(encoding="utf-8"))[oid]
            self.assertNotIn("alerta", d)                 # 3 pedidos não condenam ninguém
        finally:
            arq.unlink(missing_ok=True)
            if antes is not None:
                arq.write_text(antes, encoding="utf-8")


class TesteParecer(unittest.TestCase):
    def test_o_parecer_traz_as_sete_posicoes_e_os_numeros(self):
        p = (ROOT / "biblioteca_alexandria/PARECER-PILOTO-24H-2026-09-23.md").read_text(encoding="utf-8")
        for pos in ("Extremamente pessimista", "Pessimista", "Levemente pessimista", "Neutro",
                    "Levemente otimista", "Otimista", "Extremamente otimista"):
            self.assertIn(pos, p, pos)
        self.assertIn("9 registram", p)                   # o achado central
        self.assertIn("ele não está escolhendo", p)
        self.assertIn("38 voos", p)
        self.assertIn("Erros a corrigir", p)
