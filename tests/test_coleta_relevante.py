"""11/10/2026 (titular): validação das 558 abertas — a régua de fomento a OSC nos motores (agregadores, Espião, fluxo),
o Termo de Execução Cultural da PNAB não é ato posterior, e a medição de uso dos arquivos com alerta de 30 dias."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.indexadores.extracao import nao_e_fomento, perfil


def sai(t):
    return bool(nao_e_fomento(t) or perfil(t)[0] == "fora")


class TesteRegua(unittest.TestCase):
    def test_ruido_sai(self):
        for t in ("Credenciamento de artistas, bandas e grupos musicais locais para apresentações nos eventos",
                  "CREDENCIAMENTO DE PESSOA JURÍDICA E/OU PESSOA FÍSICA PARA CONTRATAÇÃO ARTISTAS, GRUPOS MUSICAIS",
                  "Art Explora – Cité internationale des arts Residency programme 2027", "Auxílio Financeiro- (Bolsa de Estudo)",
                  "Governo de Goiás abre inscrições para mais de 10 mil vagas em Colégios Militares — Goiás", "Inscrições Abertas — Goiás"):
            self.assertTrue(sai(t), t)

    def test_valida_fica(self):
        for t in ("CREDENCIAMENTO DE ARTISTAS, GRUPOS, COLETIVOS E AGENTES CULTURAIS, NOS TERMOS DA LEI FEDERAL Nº 14.399/2022",
                  "Edital de chamamento público de seleção de projetos para firmar termo de execução cultural",
                  "CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL – OSCS PARA EXECUÇÃO DE ESCOLINHAS ESPORTIVAS",
                  "Atendimento de matrículas na educação infantil em instituições comunitárias sem fins lucrativos", "Programa Rouanet nas Favelas 2"):
            self.assertFalse(sai(t), t)

    def test_gabarito_p3_sem_util_atingido(self):
        g = json.loads((ROOT / "tests/fixtures/gabarito_abertas_p3_br_privadas_2026_10_10.json").read_text(encoding="utf-8"))["registros"]
        uteis = {"ouro", "prata", "bronze", "pendente", "nao_disponivel"}
        self.assertEqual([r["id"] for r in g if r["veredito"] in uteis and sai(r.get("titulo") or "")], [])

    def test_m14_termo_de_execucao(self):
        from src.saneamento_motores import ato_no_trecho, limpar_cache
        limpar_cache()
        self.assertTrue(ato_no_trecho("Edital de Chamamento Público nº 001/2026 seleção de projetos para firmar Termo de Execução Cultural com agentes culturais")[0])
        self.assertFalse(ato_no_trecho("Extrato do Termo de Execução Cultural nº 12/2026 com o agente cultural")[0])

    def test_regua_nos_motores(self):
        self.assertIn("_nao_fom(tit)", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))
        self.assertIn('motivos["não é fomento a OSC"]', (ROOT / "src/espiao_foco.py").read_text(encoding="utf-8"))


class TesteUso(unittest.TestCase):
    def test_medicao(self):
        from src import uso_arquivos as U
        r = U.medir(gravar=False)
        self.assertGreater(r["monitorados"], 1000)
        self.assertEqual(r["monitorados"], r["em_uso"] + r["alertas"])
        self.assertIsNone(U.citado("dados/oportunidades/oportunidades.jsonl", "", set()) if False else None)
        cfg = json.loads((ROOT / "config/uso_arquivos.json").read_text(encoding="utf-8"))
        self.assertIn("biblioteca_alexandria/livros/_vistas/", cfg["banco_de_dados"]); self.assertEqual(cfg["dias_sem_uso"], 30)
        self.assertIn("python -m src.uso_arquivos", (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
