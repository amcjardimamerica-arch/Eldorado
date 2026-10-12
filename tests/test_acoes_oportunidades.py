"""12/10/2026 (titular): ações de volta aos cartões de Oportunidades Abertas › Em andamento (perdidas em 28/09, quando
a aba passou a mostrar os cartões do fluxo validado): ✦ Aprimorar análise com IA · ✓ Inscrição realizada · ✕ Descartar,
e o clique no cartão abre o detalhe. Decidida, a oportunidade sai de Em andamento e vai para Arquivados (inclusive as
inscritas, que antes sumiam de todas as listas); Recuperar devolve."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteAcoesOportunidades(unittest.TestCase):
    def setUp(self):
        self.h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        i = self.h.index("function _desenhaAbertasFluxo(){"); self.f = self.h[i:i + 30000]

    def test_cartao_do_fluxo_tem_as_acoes_e_o_detalhe(self):
        for marca in ('class="bt-ia"', 'class="bt-insc"', 'class="bt-desc"', 'data-oaid="', "pedirParecer(e)", "arquivarInscrito(e)", "descartarEdital(e)", "detalheEdital(e)"):
            self.assertIn(marca, self.f, marca)
        self.assertIn("function _edDoFluxo(x)", self.h)

    def test_decisao_tira_de_em_andamento(self):
        self.assertIn("inscrita/descartada sai daqui", self.f)

    def test_arquivados_inclui_inscritas_e_decididas_do_fluxo(self):
        self.assertIn("Arquivados — Inscritos / Encerrados / Descartados", self.h)
        self.assertIn('_edsDecididosDoFluxo("inscrito")', self.h); self.assertIn('_edsDecididosDoFluxo("descartado")', self.h)
        self.assertIn('["descartado","inscrito"].includes(estadoDe(e.id))', self.h)
        self.assertIn("✓ inscrição realizada", self.h)


if __name__ == "__main__":
    unittest.main()
