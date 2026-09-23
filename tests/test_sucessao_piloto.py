"""A sucessão no cargo de Piloto e as três barreiras que impediram a medição (23/09)."""
import json, pathlib, unittest
from src.cargo_piloto import CARGO, pode_assumir, deve_sair, _porque_faltou
ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8", errors="replace")


class TesteCargoVago(unittest.TestCase):
    def test_o_cargo_esta_vago_e_diz_por_que(self):
        o = json.loads(CARGO.read_text(encoding="utf-8"))["ocupante_atual"]
        self.assertTrue(o["vago"]); self.assertIsNone(o["nome"])
        self.assertEqual(o["anterior"], "Llama-3.2-3B-Instruct")
        self.assertIn("nenhum substituto medido", o["motivo"])
        self.assertIn("rede determinística", o["como_o_piloto_voa"])

    def test_vago_nao_dispara_nova_saida(self):
        self.assertFalse(deve_sair()[0])

    def test_ninguem_assume_sem_medicao(self):
        """O Qwen3 não baixou: não há número real sobre ele."""
        a = json.loads((ROOT / "estado/piloto/avaliacao-qwen3-1.7b-2026-09-23.json").read_text(encoding="utf-8"))
        self.assertIsNone(a["resultado"]["acerto"])
        self.assertIn("não disponível no runner", a["resultado"]["erro"])
        self.assertFalse(a["cumpre_criterio"])
        self.assertFalse(pode_assumir({"elegivel": False})[0])


class TesteTresBarreiras(unittest.TestCase):
    """As três tentativas de medir esbarraram em barreiras operacionais, não nos modelos."""

    def test_teto_por_modo(self):
        """Os 30 min eram do VOO e cancelaram o benchmark no meio, após 30 min de trabalho."""
        self.assertIn("TETO POR MODO", WF)
        self.assertIn("modo == 'benchmark' && 330", WF)
        self.assertIn("foi cancelado no meio", WF)

    def test_o_motivo_da_falha_de_download_fica_gravado(self):
        self.assertIn("downloads_falhos.tsv", WF)
        self.assertIn('%{http_code}', WF)
        src = (ROOT / "src/cargo_piloto.py").read_text(encoding="utf-8")
        self.assertIn("UM ERRO QUE NÃO DIZ A CAUSA CUSTA UMA RODADA INTEIRA", src)

    def test_a_leitura_do_http_e_em_portugues(self):
        a = ROOT / "estado/piloto/downloads_falhos.tsv"
        antes = a.read_text(encoding="utf-8") if a.exists() else None
        try:
            a.write_text("Qwen3-1.7B-Q4_K_M.gguf\t404\thttps://exemplo/x.gguf\n", encoding="utf-8")
            r = _porque_faltou("qwen3-1.7b")
            self.assertIn("não existe nesse endereço", r)
            a.write_text("Qwen3-1.7B-Q4_K_M.gguf\t403\thttps://exemplo/x.gguf\n", encoding="utf-8")
            self.assertIn("recusou o acesso", _porque_faltou("qwen3-1.7b"))
        finally:
            a.unlink(missing_ok=True)
            if antes is not None:
                a.write_text(antes, encoding="utf-8")

    def test_sem_registro_o_erro_diz_que_nao_sabe(self):
        a = ROOT / "estado/piloto/downloads_falhos.tsv"
        if not a.exists():
            self.assertIn("não deixou registro", _porque_faltou("qwen3-1.7b"))


class TesteParecer(unittest.TestCase):
    def test_as_sete_posicoes_e_a_recusa(self):
        p = (ROOT / "biblioteca_alexandria/pareceres/PARECER-SUCESSAO-PILOTO-2026-09-23.md").read_text(encoding="utf-8")
        for pos in ("Extremamente pessimista", "Pessimista", "Levemente pessimista", "Neutro",
                    "Levemente otimista", "Otimista", "Extremamente otimista"):
            self.assertIn(pos, p, pos)
        self.assertIn("não por falta de candidato — por falta de medição", p)
        self.assertIn("O que o conselho NÃO decidiu", p)
        self.assertIn("Não há dado", p)

    def test_o_parecer_corrige_a_nota_inventada(self):
        p = (ROOT / "biblioteca_alexandria/pareceres/PARECER-SUCESSAO-PILOTO-2026-09-23.md").read_text(encoding="utf-8")
        self.assertIn("substitutos que **eu mesmo parametrizei**", p)
        self.assertIn("nunca chegou a ser executado", p)
