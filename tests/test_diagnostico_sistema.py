"""14/10/2026 (titular): diagnóstico único do sistema (backend) — sistemas, oportunidades uma a uma, integração,
problemas com correção; --corrigir em sequência. E a curadoria não apaga livro de oportunidade aberta."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import diagnostico_sistema as D


class TesteDiagnostico(unittest.TestCase):
    def test_reune_tudo(self):
        d = D.diagnosticar()
        for k in ("sistemas", "oportunidades", "integracao", "problemas", "corrigiveis"):
            self.assertIn(k, d)
        for k in ("motores", "maestro", "rede_neural", "cartorio", "pilotos", "saude", "fluxos_github", "sala_controle"):
            self.assertIn(k, d["sistemas"])
        for k in ("abertas", "validadas", "com_livro", "sem_livro", "sem_livro_por_regra", "livro_inexistente", "sem_site_oficial", "fora_da_tela", "sem_ficha"):
            self.assertIn(k, d["oportunidades"])
        for p in d["problemas"]:
            self.assertIn(p["gravidade"], ("alta", "media", "baixa"))

    def test_backend_sem_apresentacao(self):
        self.assertTrue(str(D.SAIDA).endswith("estado/diagnostico_sistema.json")); self.assertTrue(str(D.RESUMO).startswith(str(ROOT / "estado")))
        self.assertNotIn("diagnostico_sistema", (ROOT / "docs/dashboard.html").read_text(encoding="utf-8"), "não é apresentado no painel")

    def test_correcao_em_sequencia_com_as_rotinas_do_sistema(self):
        src = (ROOT / "src/diagnostico_sistema.py").read_text(encoding="utf-8")
        for r in ("decisoes_titular.run", "opressores_repositorio.sincronizar", "repositorio_unico.construir", "fluxo_oportunidades.atualizar_mapa",
                  "fichas_oportunidades.run", "sala_controle.run", "saude.checar"):
            self.assertIn(r, src)

    def test_curadoria_protege_livro_de_aberta_e_redireciona_indice(self):
        src = (ROOT / "src/curadoria_biblioteca.py").read_text(encoding="utf-8")
        self.assertIn('fora_da_abrangencia(x) and x["id"] not in protegidos', src)
        self.assertIn('v["opressor"] = destino[v["opressor"]]', src)

    def test_fluxos(self):
        self.assertIn("python -m src.diagnostico_sistema", (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8"))
        w = (ROOT / ".github/workflows/analise-sistema.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.diagnostico_sistema --corrigir", w)


if __name__ == "__main__":
    unittest.main()
