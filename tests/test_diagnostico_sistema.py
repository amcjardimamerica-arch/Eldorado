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

    def test_so_goias_tem_municipais(self):
        """14/10 (titular, confirmado): só Goiás tem livros e oportunidades municipais; de outros estados, só estaduais."""
        from src.repositorio_unico import municipal_fora_de_goias
        self.assertTrue(municipal_fora_de_goias({"titulo": "MUNICIPIO DE ITAGIBA — Chamamento", "uf": "BA"}))
        # municípios de Goiás nunca são descartados ("para" não é Pará)
        self.assertIsNone(municipal_fora_de_goias({"titulo": "Chamamento público para fins de credenciamento", "orgao": "MUNICIPIO DE NOVA ROMA"}))
        self.assertIsNone(municipal_fora_de_goias({"titulo": "Credenciamento para oficinas", "orgao": "MUNICIPIO DE SENADOR CANEDO"}))
        self.assertTrue(municipal_fora_de_goias({"titulo": "Diário Oficial de Londrina (PR) — chamamento", "orgao": "Prefeitura de Londrina", "uf": "PR"}))
        self.assertIsNone(municipal_fora_de_goias({"titulo": "Diário Oficial de Curitiba (PR) — chamamento", "orgao": "Prefeitura de Curitiba", "uf": "PR"}))   # capital fica
        self.assertIsNone(municipal_fora_de_goias({"titulo": "Edital estadual", "orgao": "Secretaria de Estado da Cultura de São Paulo", "nivel": "estadual", "uf": "SP"}))
        rep = (ROOT / "src/repositorio_unico.py").read_text(encoding="utf-8")
        self.assertIn('"descartada: oportunidade municipal de outro estado', rep)
        cur = (ROOT / "src/curadoria_biblioteca.py").read_text(encoding="utf-8")
        self.assertIn('fora = [x for x in ms if fora_da_abrangencia(x)]', cur); self.assertIn("ARQ.unlink()", cur)   # 14/10: apagados, sem arquivo
        self.assertNotIn('"recuperado_por"', cur)
        self.assertIn("só Goiás tem livros municipais", (ROOT / "src/opressores_repositorio.py").read_text(encoding="utf-8"))
        self.assertIn('_m.get("id") in _arq or', (ROOT / "src/motores.py").read_text(encoding="utf-8"))
        d = D.diagnosticar()["oportunidades"]
        self.assertIn("municipais_de_outro_estado_abertas", d); self.assertIn("livros_municipais_de_outro_estado", d)

    def test_execucao_finalidade_e_sala(self):
        d = D.diagnosticar()
        for k in ("finalidade", "execucao", "sala_de_controle"):
            self.assertIn(k, d)
        nomes = {x["sistema"] for x in d["finalidade"]["sistemas"]}
        self.assertTrue({"Motores", "Maestro", "Rede neural", "Biblioteca", "Validação", "Cartório", "Fluxos automáticos"} <= nomes)
        for x in d["finalidade"]["sistemas"]:
            self.assertIn(x["estado"], ("ok", "atencao", "falha", "sem_dados"))
        for k in ("divergencias", "sem_leitura", "estados_incoerentes", "sugestoes_de_apresentacao"):
            self.assertIn(k, d["sala_de_controle"])
        self.assertEqual(D._cadencia_h('cron: "13 0,9,12,15,18,21 * * *"'), 3.0)
        self.assertEqual(D._cadencia_h('cron: "23 6 * * *"'), 24.0)

    def test_fluxos(self):
        self.assertIn("python -m src.diagnostico_sistema", (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8"))
        w = (ROOT / ".github/workflows/analise-sistema.yml").read_text(encoding="utf-8")
        self.assertIn("python -m src.diagnostico_sistema --corrigir", w)


if __name__ == "__main__":
    unittest.main()
