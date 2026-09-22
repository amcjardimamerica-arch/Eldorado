"""O avião não fica parado num canto: atravessa a faixa onde o Piloto trabalha (22/09)."""
import pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")


class TesteAviaoEmTravessia(unittest.TestCase):
    def test_vai_e_volta_virando_o_nariz(self):
        kf = re.search(r"@keyframes pil-travessia\{[\s\S]*?\}\}", H)
        self.assertTrue(kf, "falta a animação de travessia")
        k = kf.group(0)
        self.assertEqual(len(re.findall(r"scaleX\(-1\)", k)), 2)          # vira na ida e desvira na volta
        self.assertIn("var(--pil-dist", k)                                 # a distância é a largura da faixa
        self.assertTrue(re.search(r"100%[^}]*scaleX\(1\)", k))             # fecha o ciclo olhando para a frente
        self.assertIn("animation:pil-travessia var(--pil-tempo", H)
        self.assertNotIn("pil-passeia", H)                                 # a animação antiga saiu

    def test_a_faixa_e_o_lugar_do_trabalho(self):
        self.assertIn('cacar_oportunidade:["#rank-apoiadores"', H)         # caçando → cruza o ranking
        self.assertIn('afiar_motor:["#pil-posto-bussola"', H)
        self.assertIn('resgate:["#pil-posto"', H)                          # missão especial tem faixa própria
        self.assertIn("--pil-dist", H); self.assertIn("--pil-tempo", H)
        self.assertIn("travessia/26", H)                                    # velocidade constante, faixa larga = voo longo

    def test_nenhum_aviao_parado_no_canto(self):
        self.assertNotIn('<h4>${aviaoDoPiloto(', H)                         # saiu o avião fixo do cabeçalho
        self.assertNotIn("voa?aviaoDoPiloto", H)                            # e o que ficava em cada motor
        self.assertEqual(len(re.findall(r"aviaoDoPiloto\(", H)), 2)         # só a definição e o que viaja
        self.assertIn("pil-voando-ic", H)                                   # no cabeçalho ficou só um ícone

    def test_balao_nao_vira_junto_com_o_aviao(self):
        self.assertIn('</div>` +\n      `<span class="pil-balao">', H)      # o balão está fora do que gira
        self.assertIn(".pil-balao{position:absolute;right:0", H)

    def test_patrulha_quando_nao_ha_missao(self):
        self.assertIn("patrulha", H)
        self.assertIn("ele patrulha a última faixa conhecida", H)
