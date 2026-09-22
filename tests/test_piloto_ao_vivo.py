"""O painel do Piloto não pode ser decorativo (auditoria de 22/09)."""
import json, pathlib, re, unittest
from datetime import datetime, timedelta, timezone
from src.piloto_ao_vivo import montar, marcar, SEM_SINAL_MIN, VIVO
from src.missao_especial import _relevante, montar_fila
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")


class TesteEstadoAoVivo(unittest.TestCase):
    def test_diz_o_que_esta_fazendo_agora(self):
        d = montar()
        for c in ("estado", "frase", "sinal_em", "minutos_sem_sinal", "missao_atual",
                  "ultima_missao", "voos_hoje", "missoes_com_achado", "resgate", "pode_acionar"):
            self.assertIn(c, d, c)
        self.assertIn(d["estado"], ("em_voo", "pousado", "parado", "pausado_pelo_titular"))

    def test_tudo_tem_carimbo_para_o_painel_julgar(self):
        d = montar()
        self.assertTrue(d["em"]); self.assertEqual(d["sem_sinal_a_partir_de_min"], SEM_SINAL_MIN)
        # o painel recalcula pelo relógio de quem olha, em vez de confiar no rótulo gravado
        self.assertIn("o painel NÃO confia no rótulo gravado", H)
        self.assertIn("V.sem_sinal_a_partir_de_min", H)

    def test_mostra_o_motor_ligado(self):
        self.assertIn('motor <b>${esc(M.motor||M.alvo||"—")}</b>', H)
        self.assertIn("EM VOO", H); self.assertIn("SEM SINAL", H); self.assertIn("POUSADO", H)

    def test_oferece_acionamento_quando_parado(self):
        self.assertIn("pil-bt-acionar", H); self.assertIn("acionar o Piloto", H)
        self.assertIn('est==="parado"?`<div class="pil-acionar">', H)   # só quando parado
        self.assertIn("workflows/sindico.yml", H)

    def test_numeros_reais_e_nao_enfeite(self):
        for x in ("voo(s) hoje", "com achado", "a resgatar", "resgatado(s)", "abate(s)"):
            self.assertIn(x, H, x)
        self.assertIn("Última missão:", H)                               # inclusive quando falhou

    def test_marcar_registra_passo_do_voo(self):
        antes = VIVO.read_text(encoding="utf-8") if VIVO.exists() else None
        try:
            d = marcar("entrou_no_motor", motor="motor-gife", detalhe="x")
            self.assertEqual(d["evento"], "entrou_no_motor")
            self.assertEqual(d["historico"][0]["motor"], "motor-gife")
        finally:
            if antes: VIVO.write_text(antes, encoding="utf-8")


class TesteCorrecoesDaAuditoria(unittest.TestCase):
    def test_ordem_dos_buscadores_segue_a_medicao(self):
        from src.piloto_busca import BUSCADORES, ESPERA_ENTRE_BUSCAS
        self.assertEqual(BUSCADORES[0][0], "duckduckgo")                 # o único que respondeu
        self.assertGreaterEqual(ESPERA_ENTRE_BUSCAS, 3)                  # não metralha o buscador
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn("não gasta tempo com os mortos", src)

    def test_fila_so_aceita_edital_que_serve(self):
        self.assertFalse(_relevante({"titulo": "CHAMAMENTO PARA CREDENCIAMENTO DE LEILOEIROS OFICIAIS"})[0])
        self.assertFalse(_relevante({"titulo": "cadastrar Profissionais de saúde"})[0])
        self.assertFalse(_relevante({"titulo": "aquisição de medicamentos"})[0])
        ok, porque = _relevante({"titulo": "Seleção de propostas para celebração de parceria com OSC"})
        self.assertTrue(ok); self.assertIn("serve", porque)
        self.assertTrue(_relevante({"titulo": "Edital de fomento à cultura"})[0])
        r = montar_fila()
        self.assertGreater(sum(r["descartados_por_nao_servirem"].values()), 10)
        self.assertLess(r["total_incompletos"], 200)                     # de 438 para menos de 200

    def test_parecer_do_conselho_existe_com_as_sete_posicoes(self):
        p = (ROOT / "biblioteca_alexandria/PARECER-CONSELHO-PILOTO-2026-09-22.md").read_text(encoding="utf-8")
        for pos in ("Extremamente pessimista", "Pessimista", "Levemente pessimista", "Neutro",
                    "Levemente otimista", "Otimista", "Extremamente otimista"):
            self.assertIn(pos, p, pos)
        self.assertIn("não está cumprindo a finalidade", p)              # o veredito, sem atenuação
        self.assertIn("72 horas", p)                                     # com prazo e número objetivo
        self.assertGreaterEqual(len(re.findall(r"^\| \d+ \|", p, re.M)), 12)   # cada erro listado

    def test_abate_de_laboratorio_saiu_do_painel(self):
        b = json.loads((ROOT / "estado/sindico/bordo.json").read_text(encoding="utf-8"))
        self.assertNotIn("lab-motor", b.get("abates") or {})
        self.assertEqual(b["total_abates"], sum(v.get("n", 0) for v in (b.get("abates") or {}).values()))
