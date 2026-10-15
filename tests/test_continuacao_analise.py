"""14/10/2026 (continuação da análise do sistema): adiados passam à frente na fila dos motores; fluxos 34 e 36 gravam
com reserva e o 36 tem grupo próprio; a sala de controle mostra os sistemas que faltavam e trata 'sem valor' como
'sem leitura'."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))


class TesteContinuacao(unittest.TestCase):
    def test_adiados_passam_a_frente(self):
        src = (ROOT / "scripts/motores_da_vez.py").read_text(encoding="utf-8")
        self.assertIn("key=lambda m: (m not in adiados,", src)

    def test_gravacao_com_reserva_e_grupo_proprio(self):
        for arq in ("motores-empresas.yml", "analise-sistema.yml"):
            w = (ROOT / ".github/workflows" / arq).read_text(encoding="utf-8")
            # 15/10/2026 (ciclo 5): a reaplicação da árvore inteira apagava dados de outros fluxos — agora cada fluxo grava
            # só os arquivos que alterou, por cima do main mais recente (scripts/gravar_somente_alterados.py)
            self.assertIn("python scripts/gravar_somente_alterados.py salvar", w, arq)
            self.assertIn("python scripts/gravar_somente_alterados.py aplicar", w, arq)
            self.assertNotIn("git reset -q --mixed origin/main", w, arq)
        self.assertIn("group: analise-sistema", (ROOT / ".github/workflows/analise-sistema.yml").read_text(encoding="utf-8"))

    def test_sala_mostra_o_que_faltava(self):
        from src import sala_controle as S
        ids = {x["id"] for x in S.montar()["instrumentos"]}
        self.assertTrue({"es_validadas", "es_fichas", "de_decisoes", "al_externa", "dg_finalidade"} <= ids)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for i in ("es_validadas", "es_fichas", "de_decisoes", "al_externa", "dg_finalidade"):
            self.assertIn(f'"{i}"', h, i)

    def test_sem_valor_e_sem_leitura(self):
        from src import sala_controle as S
        self.assertEqual(S._estado(1.0, 2, None, {"normal": [80, None]})[0], "cinza")


if __name__ == "__main__":
    unittest.main()
