"""Por que o Qwen3-1.7B nunca foi medido, e a regra de permanência que faltava (23/09)."""
import json, pathlib, unittest
from src.piloto import CANDIDATOS, _candidatos
from src.cargo_piloto import pode_assumir, deve_sair, cargo_vago, CARGO
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteUmaListaSo(unittest.TestCase):
    """Havia duas: a do benchmark, fixa no código, e o banco de reserva do cargo. Por isso o
    Qwen3-1.7B estava no banco desde 21/09 e NUNCA foi medido — o benchmark não o via."""

    def test_o_banco_de_reserva_inteiro_entra_no_benchmark(self):
        c = json.loads(CARGO.read_text(encoding="utf-8"))
        nomes = {x["nome"] for x in CANDIDATOS}
        for r in c["banco_de_reserva"]:
            self.assertIn(r["nome"], nomes, f"{r['nome']} ficaria de fora do benchmark")

    def test_o_qwen3_esta_na_lista(self):
        self.assertTrue(any("Qwen3" in (c["nome"] or "") for c in CANDIDATOS))
        q = next(c for c in CANDIDATOS if "Qwen3" in (c["nome"] or ""))
        self.assertTrue(q["url"].endswith(".gguf"))
        self.assertEqual(q["licenca"], "Apache-2.0")
        self.assertLess(q["gb"], 3.0)   # o 4B tem 2,5 GB                       # 1,1 GB: cabe no runner

    def test_so_modelos_qwen(self):
        """24/09 (titular): a família é Qwen; o llama.cpp é só o executor."""
        self.assertTrue(all("qwen" in c["nome"].lower() for c in CANDIDATOS))
    def test_candidato_sem_url_nao_entra(self):
        self.assertTrue(all(c.get("url") for c in _candidatos()))

    def test_a_razao_do_defeito_esta_escrita(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("DUAS LISTAS QUE NÃO CONVERSAVAM", src)
        self.assertIn("NUNCA foram medidos", src)


class TestePermanencia(unittest.TestCase):
    """Entrar tinha critério; permanecer, não. Um ocupante medido em 0,342 seguiu voando
    um dia e meio depois da medição que o reprovou."""

    def test_quem_nao_responde_em_voo_sai(self):
        """O cargo está vago desde 23/09, então o caso é construído: a regra vale para
        qualquer ocupante, não para um em particular."""
        antes = CARGO.read_text(encoding="utf-8")
        try:
            c = json.loads(antes)
            c["ocupante_atual"] = {"nome": "X", "id": "x",
                                   "desempenho_em_voo": {"pedidos": 40, "taxa_de_resposta": 0.24}}
            CARGO.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
            sai, porque = deve_sair()
            self.assertTrue(sai)
            self.assertIn("abaixo dos 50%", porque)
        finally:
            CARGO.write_text(antes, encoding="utf-8")

    def test_prazo_inventado_derruba(self):
        antes = CARGO.read_text(encoding="utf-8")
        try:
            c = json.loads(antes)
            c["ocupante_atual"] = {"nome": "X", "id": "x",
                                   "desempenho_em_voo": {"pedidos": 20, "taxa_de_resposta": 0.9}}
            CARGO.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
            sai, porque = deve_sair({"acerto": 0.95, "prazos_inventados": 2})
            self.assertTrue(sai); self.assertIn("eliminatória", porque)
            sai, porque = deve_sair({"acerto": 0.34, "prazos_inventados": 0})
            self.assertTrue(sai); self.assertIn("34", porque)
            sai, porque = deve_sair({"acerto": 0.7, "prazos_inventados": 0})
            self.assertFalse(sai); self.assertIn("cumpre", porque)
        finally:
            CARGO.write_text(antes, encoding="utf-8")

    def test_amostra_pequena_nao_condena(self):
        antes = CARGO.read_text(encoding="utf-8")
        try:
            c = json.loads(antes)
            c["ocupante_atual"] = {"nome": "X", "id": "x",
                                   "desempenho_em_voo": {"pedidos": 4, "taxa_de_resposta": 0.0}}
            CARGO.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
            self.assertFalse(deve_sair({"acerto": 0.8})[0])   # 4 pedidos não decidem nada
        finally:
            CARGO.write_text(antes, encoding="utf-8")

    def test_cargo_vago_nao_dispara_saida(self):
        antes = CARGO.read_text(encoding="utf-8")
        try:
            cargo_vago("teste")
            self.assertFalse(deve_sair()[0])
        finally:
            CARGO.write_text(antes, encoding="utf-8")


class TesteRegistroCorrigido(unittest.TestCase):
    def test_o_codigo_corrige_o_que_eu_escrevi_errado(self):
        """Escrevi que o Llama foi nomeado sem passar no benchmark. Ele venceu o benchmark 1
        com 0,597. O erro foi não removê-lo quando caiu para 0,342 no benchmark 2."""
        src = (ROOT / "src/cargo_piloto.py").read_text(encoding="utf-8")
        self.assertIn("CORREÇÃO DO REGISTRO", src)
        self.assertIn("0,597", src)
        self.assertIn("A nomeação", src); self.assertIn("foi legítima", src)
        self.assertIn("regra para demitir", src)

