"""Missões especiais de resgate e voo sob demanda (22/09)."""
import json, pathlib, unittest
from src.missao_especial import (montar_fila, proximo, plano_de_voo, registrar_resgate,
                                 publicar, _falta, _urgencia, MINIMO, FILA)
ROOT = pathlib.Path(__file__).resolve().parents[1]


class _IA:
    def __init__(self, r): self.r = r; self.perguntas = []
    def perguntar(self, p, esquema=None): self.perguntas.append(p); return self.r


class TesteFilaDeResgate(unittest.TestCase):
    def test_o_que_falta_para_um_edital_servir(self):
        self.assertEqual(set(MINIMO), {"pagina_oficial", "prazo", "quem_pode", "documentos", "valor", "como_inscrever"})
        vazio = _falta({"titulo": "x"})
        self.assertEqual(len(vazio), 6)
        cheio = _falta({"pagina_oficial": "u", "prazo": "2026-12-01", "quem_pode": "OSC",
                        "documentos": ["estatuto"], "valor": "R$ 50 mil", "como_inscrever": "formulário"})
        self.assertEqual(cheio, [])

    def test_urgencia_prioriza_goias_e_prazo_aberto(self):
        f = ["pagina_oficial", "prazo"]
        base = _urgencia({"uf": "SP"}, f)
        self.assertGreater(_urgencia({"uf": "GO"}, f), base)                       # Goiás pesa mais
        self.assertGreater(_urgencia({"uf": "SP", "prazo": "2099-01-01"}, f), base)  # ainda dá tempo
        self.assertGreater(_urgencia({"uf": "SP", "veredito": "aprovado"}, f), base)

    def test_fila_montada_do_acervo_real(self):
        r = montar_fila()
        # caiu de 438 para 39 com os filtros de objeto e de credenciamento (23/09)
        self.assertGreater(r["total_incompletos"], 20)
        self.assertLessEqual(r["na_fila"], 60)
        self.assertIn("ANTES de explorar", r["regra"])
        p = proximo(reservar=False)                                                # espiar não reserva
        self.assertTrue(p and p.get("falta") and p.get("titulo"))
        self.assertEqual(p["estado"], "aguardando")
        a = proximo(); b = proximo()                                               # reservar dá itens DIFERENTES
        self.assertNotEqual(a["id"], b["id"], "sem reserva o voo sairia com um resgate só")
        from src.missao_especial import devolver_a_fila
        devolver_a_fila(a["id"]); devolver_a_fila(b["id"])
        self.assertEqual(proximo(reservar=False)["estado"], "aguardando")           # devolvidos à fila

    def test_plano_de_voo_da_missao_especial(self):
        ia = _IA({"consultas": ["edital fundo municipal saúde página oficial"],
                  "onde_provavelmente_esta": "portal do município", "o_que_ler_na_pagina": ["prazo"]})
        alvo = {"id": "x1", "titulo": "Chamamento público 03/2026", "orgao": "Fundo Municipal", "falta": ["prazo", "documentos"]}
        pl = plano_de_voo(ia, alvo)
        self.assertEqual(pl["origem"], "missao_especial")
        self.assertTrue(pl["consultas_sugeridas"])
        self.assertIn("prazo", pl["pergunta"])
        p = ia.perguntas[0]
        self.assertIn("MISSÃO ESPECIAL", p); self.assertIn("PÁGINA OFICIAL", p)
        self.assertIn("não a notícia sobre ele", p)

    def test_resgate_conclui_e_vira_ficha_na_biblioteca(self):
        antes = FILA.read_text(encoding="utf-8")
        try:
            d = json.loads(antes)
            k = next(k for k, v in d["itens"].items() if v.get("estado") in ("aguardando", "em_resgate"))
            it = registrar_resgate(k, {"pagina_oficial": "https://x.gov.br/edital", "prazo": "2099-01-01",
                                       "quem_pode": "OSC", "documentos": ["estatuto", "CNPJ"],
                                       "valor": "R$ 100 mil", "como_inscrever": "formulário online"}, True)
            self.assertEqual(it["estado"], "resgatado"); self.assertEqual(it["falta"], [])
            self.assertGreaterEqual(it["tentativas"], 1)
            n = it["tentativas"]
            it2 = registrar_resgate(k, {}, False)                                  # tentativa falha conta
            self.assertEqual(it2["tentativas"], n + 1)
            self.assertIn("por_estado", publicar())
        finally:
            FILA.write_text(antes, encoding="utf-8")

    def test_desiste_depois_de_tres_tentativas(self):
        antes = FILA.read_text(encoding="utf-8")
        try:
            d = json.loads(antes)
            k = next(iter(d["itens"]))
            for _ in range(3):
                it = registrar_resgate(k, {}, False)
            self.assertEqual(it["estado"], "sem_sucesso")
        finally:
            FILA.write_text(antes, encoding="utf-8")


class TestePrioridadeETempo(unittest.TestCase):
    def test_resgate_vem_antes_da_exploracao(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertLess(src.index("montar_fila()"), src.index("plano += sortear()"))
        self.assertIn('plano.append({"tipo": "resgate"', src)
        self.assertIn("PRIMEIRO os resgates", src)
        self.assertIn("def missao_resgate", src)
        cg = json.loads((ROOT / "config/cargo_piloto.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(cg["parametros"]["resgates_por_voo"], 3)
        self.assertIn("primeiro", cg["parametros"]["prioridade"])   # verificar e alimentar antes de explorar

    def test_voo_dura_o_que_a_tarefa_exigir(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("O VOO DURA O QUE A TAREFA EXIGIR", src)
        self.assertIn("teto_s", src); self.assertNotIn("limite_s", src)
        self.assertIn('rel["encerrou_por"] = "teto de tempo"', src)
        self.assertIn('rel.setdefault("encerrou_por", "tarefa concluída")', src)
        self.assertIn('rel["minutos_de_voo"]', src)
        c = json.loads((ROOT / "config/piloto.json").read_text(encoding="utf-8"))
        self.assertLessEqual(c["orcamento"]["teto_minutos"], 28)                   # cabe nos 30 do job
        self.assertIn("nao uma meta", c["orcamento"]["regra_de_tempo"])
        self.assertNotIn("minutos_por_ciclo", c["orcamento"])

    def test_resgate_nao_inventa_dado(self):
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("Não invente data nem documento", src)
        self.assertIn("trecho inventado: não aceito", src)                          # confere na página
        self.assertIn('re.fullmatch', src)                                          # prazo só em formato de data
        self.assertIn('d{4}-', src)

    def test_briefing_sabe_da_fila(self):
        from src.briefing_piloto import _estado_do_banco
        b = _estado_do_banco()
        self.assertIn("editais_incompletos_na_fila", b)
        src = (ROOT / "src/briefing_piloto.py").read_text(encoding="utf-8")
        self.assertIn("Eles são atendidos ANTES desta exploração", src)

    def test_painel_mostra_as_missoes_especiais(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("pil-resg", "Missões especiais", "carregaResgates", "pil-urg"):
            self.assertIn(x, h, x)
