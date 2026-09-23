"""A trilha do cargo e a regra de que reprovado não assume (23/09)."""
import json, pathlib, unittest
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.trilha_do_cargo import PROVAS, Substituto, correr, TETO_S, ALVO_S
from src.cargo_piloto import pode_assumir, cargo_vago, CARGO
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteAsProvasSaoAsRegrasEmVigor(unittest.TestCase):
    def test_cada_regra_ja_fixada_virou_prova(self):
        ids = {p["id"] for p in PROVAS}
        for r in ("briefing", "pncp_fora", "uma_vez", "reconhecimento",
                  "quem_pagou", "nao_inventa", "reinicio", "aprende"):
            self.assertIn(r, ids, r)
        self.assertEqual(sum(p["peso"] for p in PROVAS), 100)
        for p in PROVAS:
            self.assertTrue(p["o_que_mede"] and p["porque"], p["id"])
            self.assertTrue(p["pergunta"] and p["esquema"], p["id"])

    def test_as_duas_eliminatorias_sao_as_certas(self):
        elim = {p["id"] for p in PROVAS if p["eliminatoria"]}
        self.assertEqual(elim, {"nao_inventa", "reinicio"})
        # inventar prazo suja a Biblioteca; não reiniciar quebra a corrente
        self.assertIn("suja a Biblioteca", next(p["porque"] for p in PROVAS if p["id"] == "nao_inventa"))
        self.assertIn("corrente para", next(p["porque"] for p in PROVAS if p["id"] == "reinicio"))

    def test_o_gabarito_recusa_o_erro_certo(self):
        c = {p["id"]: p["corrige"] for p in PROVAS}
        self.assertTrue(c["nao_inventa"]({"prazo": None}))
        self.assertFalse(c["nao_inventa"]({"prazo": "2026-12-31"}))        # inventou
        self.assertTrue(c["reinicio"]({"acao": "chamar_proximo", "segundos": 3}))
        self.assertFalse(c["reinicio"]({"acao": "aguardar_cron", "segundos": 7200}))
        self.assertTrue(c["pncp_fora"]({"1": "do_claude", "2": "do_piloto",
                                        "3": "do_claude", "4": "do_piloto"}))
        self.assertFalse(c["reconhecimento"]({"consultas": ["editais abertos PNCP", "licitação"]}))
        self.assertTrue(c["aprende"]({"destino": "do_claude"}))


class TesteJulgamentoJusto(unittest.TestCase):
    def test_quem_cala_nao_e_eliminado(self):
        """Silêncio não é mentira: um modelo mudo não inventou prazo."""
        mudo = Substituto("mudo total", responde=0.0, acerta=1.0, s_medio=1.0, semente=1)
        r = correr(mudo, mostrar=False)
        self.assertEqual(r["eliminado_por"], [])
        self.assertIn("nao_inventa", r["nao_provou"])
        self.assertFalse(r["elegivel"])                                     # mas não aprova

    def test_quem_inventa_prazo_e_eliminado(self):
        m = Substituto("inventor", responde=1.0, acerta=1.0, s_medio=1.0,
                       inventa_prazo=True, semente=2)
        r = correr(m, mostrar=False)
        self.assertIn("nao_inventa", r["eliminado_por"])
        self.assertFalse(r["elegivel"])

    def test_eliminatoria_tem_tres_chances(self):
        src = (ROOT / "scripts/trilha_do_cargo.py").read_text(encoding="utf-8")
        self.assertIn("TRÊS CHANCES NA ELIMINATÓRIA", src)
        self.assertIn("perde o cargo por azar", src)
        r = correr(Substituto("quase sempre responde", 0.6, 1.0, 1.0, semente=7), mostrar=False)
        self.assertEqual(r["provas"][0]["tentativas_possiveis"], 1)          # briefing: tiro único
        el = [l for l in r["provas"] if l["eliminatoria"]]
        self.assertTrue(all(l["tentativas_possiveis"] == 3 for l in el))

    def test_velocidade_conta_mas_nao_decide_sozinha(self):
        rapido_errado = correr(Substituto("rápido e errado", 1.0, 0.3, 0.3, semente=3), mostrar=False)
        lento_certo = correr(Substituto("certeiro e lento", 1.0, 1.0, 9.0, semente=4), mostrar=False)
        self.assertGreater(lento_certo["nota"], rapido_errado["nota"])
        # mas a lentidão cobra seu preço
        certeiro_rapido = correr(Substituto("certeiro e rápido", 1.0, 1.0, 1.0, semente=5), mostrar=False)
        self.assertGreater(certeiro_rapido["nota"], lento_certo["nota"])

    def test_quem_estoura_o_teto_por_pergunta_nao_passa(self):
        r = correr(Substituto("lentíssimo", 1.0, 1.0, TETO_S * 2.5, semente=6), mostrar=False)
        self.assertTrue(r["estourou_teto"])
        self.assertFalse(r["elegivel"])
        self.assertLess(ALVO_S, TETO_S)


class TesteCargoNaoAceitaReprovado(unittest.TestCase):
    """Em 21/09 o benchmark terminou sem vencedor e o Llama foi posto no cargo assim mesmo."""

    def test_recusa_eliminado_e_quem_nao_provou(self):
        self.assertFalse(pode_assumir({"eliminado_por": ["nao_inventa"], "elegivel": False})[0])
        self.assertFalse(pode_assumir({"nao_provou": ["reinicio"], "elegivel": False})[0])
        self.assertFalse(pode_assumir({})[0])
        self.assertFalse(pode_assumir({"elegivel": True, "taxa_de_resposta": 0.12})[0])

    def test_aceita_o_elegivel(self):
        ok, porque = pode_assumir({"elegivel": True, "taxa_de_resposta": 0.95, "nota": 0.82})
        self.assertTrue(ok); self.assertIn("elegível", porque)

    def test_o_cargo_pode_ficar_vago_e_diz_como_o_piloto_voa(self):
        antes = CARGO.read_text(encoding="utf-8")
        try:
            v = cargo_vago("nenhum candidato elegível na trilha")
            self.assertTrue(v["vago"]); self.assertIsNone(v["nome"])
            self.assertIn("rede determinística", v["como_o_piloto_voa"])
            # 'anterior' só existe se havia ocupante: com o cargo já vago desde 23/09,
            # não há de quem herdar, e inventar um nome ali seria pior que o campo nulo
            self.assertIn("anterior", v)
        finally:
            CARGO.write_text(antes, encoding="utf-8")

    def test_a_razao_da_regra_esta_escrita(self):
        src = (ROOT / "src/cargo_piloto.py").read_text(encoding="utf-8")
        self.assertIn("O CARGO NÃO ACEITA REPROVADO", src)
        self.assertIn("disfarçado de inteligência", src)
        self.assertIn("CORREÇÃO DO REGISTRO", src)           # o motivo real, corrigido em 23/09
