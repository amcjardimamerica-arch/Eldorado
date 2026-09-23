"""Voo permanente: 3 s no pátio, briefing de contexto e leitura do edital (22/09)."""
import json, pathlib, unittest, yaml
from src.briefing_piloto import _estado_do_banco, escrever, fechar, anteriores, publicar
ROOT = pathlib.Path(__file__).resolve().parents[1]


class _IA:
    def __init__(self, r): self.r = r; self.perguntas = []
    def perguntar(self, p, esquema=None): self.perguntas.append(p); return self.r


class TesteCicloDeTresSegundos(unittest.TestCase):
    def test_pousa_e_decola_em_tres_segundos(self):
        w = yaml.safe_load((ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8"))
        txt = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("Pousar 3 segundos e decolar de novo", txt)
        self.assertIn("sleep 3", txt)
        job = list(w["jobs"].values())[0]
        # o teto virou expressão por modo em 23/09 — o benchmark precisa de mais que um voo.
        # O que se cobra é que o VOO continue em 30: é ele que não pode monopolizar o runner.
        teto = str(job["timeout-minutes"])
        self.assertIn("||30", teto.replace(" ", "")) if "$" in teto else self.assertLessEqual(int(teto), 30)
        self.assertIn("benchmark", teto) if "$" in teto else None                    # uma pesquisa por execução
        c = json.loads((ROOT / "config/piloto.json").read_text(encoding="utf-8"))
        self.assertEqual(c["encadeamento"]["pausa_no_patio_s"], 3)
        self.assertEqual(c["encadeamento"]["teto_execucao_min"], 30)
        self.assertLessEqual(c["orcamento"]["teto_minutos"], 28)            # teto, não meta: cabe nos 30 do job

    def test_travas_para_nao_estourar_o_github(self):
        txt = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("estado/piloto_pausado", txt)                          # o titular segura o Piloto
        self.assertIn("teto do dia atingido", txt)
        self.assertIn("in_progress", txt)                                    # nunca dois voos no ar
        self.assertIn("github.run_id", txt)                                  # não conta a si mesmo


class TesteBriefing(unittest.TestCase):
    def test_le_o_banco_antes_de_decolar(self):
        b = _estado_do_banco()
        self.assertGreater(b["editais_no_banco"], 100)
        for c in ("oportunidades_abertas", "arquivadas", "por_uf", "orgaos_mais_frequentes", "apoiadores_mapeados"):
            self.assertIn(c, b, c)

    def test_escreve_diagnostico_aposta_e_prompt(self):
        ia = _IA({"diagnostico": "só temos fonte pública", "aposta": {"onde": "energia em GO", "porque": "concessionária tem obrigação socioambiental", "confianca": "alta"},
                  "pergunta_de_pesquisa": "que concessionárias de energia em Goiás têm edital socioambiental?",
                  "o_que_procurar": ["site oficial"], "nivel": "regional"})
        b = escrever(ia)
        self.assertEqual(b["aposta"]["onde"], "energia em GO")
        self.assertTrue(b["pergunta_de_pesquisa"])
        p = ia.perguntas[0]
        self.assertIn("O QUE A BIBLIOTECA TEM HOJE", p)
        self.assertIn("caça a FONTE do dinheiro", p)
        b2 = fechar(b, [{"titulo": "Edital X", "url": "https://x.org", "situacao": "aberta"}], abertas=1)
        self.assertEqual(b2["resultado"]["achados"], 1)
        self.assertTrue(anteriores())
        self.assertIn("total", publicar())

    def test_voo_nao_sai_sem_pergunta(self):
        b = escrever(_IA(None))                                              # modelo mudo
        self.assertTrue(b["pergunta_de_pesquisa"])
        self.assertEqual(b["aposta"]["confianca"], "baixa")

    def test_briefing_alimenta_o_voo_seguinte(self):
        ia = _IA({"diagnostico": "d", "aposta": {"onde": "bancos", "porque": "p", "confianca": "media"},
                  "pergunta_de_pesquisa": "q", "nivel": "nacional"})
        escrever(ia)
        p = ia.perguntas[0]
        self.assertIn("VOOS ANTERIORES", p)                                  # lê o que já fez
        self.assertIn("JÁ APOSTEI NESTES LUGARES", p)                        # e não repete
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("_brief(ia)", src); self.assertIn("_fechar(brief", src)


class TesteLeituraDoEdital(unittest.TestCase):
    def test_piloto_le_prazo_documentos_e_classifica(self):
        src = (ROOT / "src/piloto_busca.py").read_text(encoding="utf-8")
        self.assertIn('"situacao": "aberta|arquivada|sem_prazo_na_pagina"', src)
        self.assertIn('"documentos"', src); self.assertIn('"recorrente"', src)
        self.assertIn("a data manda", src)                                   # prazo escrito vence o rótulo do modelo
        self.assertIn("indica que o financiador costuma abrir de novo", src)  # arquivada ainda serve

    def test_posto_do_piloto_em_dois_lugares(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertEqual(h.count('id="pil-posto"'), 1)
        self.assertEqual(h.count('id="pil-posto-bussola"'), 1)
        self.assertNotIn("voa?aviaoDoPiloto", h)                             # nenhum avião solto nos motores
        self.assertIn("pil-brief", h)                                        # o plano do voo aparece no posto
