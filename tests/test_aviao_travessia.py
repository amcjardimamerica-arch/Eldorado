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


class TestePostoSoEmDuasPaginas(unittest.TestCase):
    """A CAUSA de a caixa aparecer em toda página: a seção v-piloto-posto não estava em
    VISTAS, então trocaVista() nunca lhe punha a classe 'oculto'. Mudar a caixa de lugar
    no arquivo não resolvia — ela seguia visível em qualquer aba."""

    def test_o_posto_entra_no_controle_de_abas(self):
        self.assertIn('const pp=$("v-piloto-posto"); if(pp)pp.classList.toggle("oculto", v!=="inicio");', H)
        # e continua fora de VISTAS de propósito: não é uma vista, é o rodapé da inicial
        vistas = re.search(r"const VISTAS=\[([^\]]*)\]", H).group(1)
        self.assertNotIn("piloto-posto", vistas)

    def test_existe_um_posto_em_cada_uma_das_duas_paginas(self):
        self.assertEqual(H.count('id="pil-posto"'), 1)
        self.assertEqual(H.count('id="pil-posto-bussola"'), 1)

    def test_o_posto_fica_no_fim_das_duas_paginas(self):
        L = H.split("\n")
        i_cal = next(k for k, l in enumerate(L) if 'id="v-calendario"' in l)
        i_posto = next(k for k, l in enumerate(L) if 'id="v-piloto-posto"' in l)
        self.assertGreater(i_posto, i_cal, "na inicial o posto vem depois do calendário")
        i_bus = next(k for k, l in enumerate(L) if 'id="v-bussola"' in l)
        i_pb = next(k for k, l in enumerate(L) if 'id="pil-posto-bussola"' in l)
        fim_bus = next(k for k, l in enumerate(L) if k > i_pb and l.strip() == "</section>")
        self.assertTrue(i_bus < i_pb < fim_bus)
        self.assertEqual(fim_bus, i_pb + 1, "na Bússola o posto é a última coisa da seção")

    def test_texto_do_rodape_nao_fala_mais_de_horarios(self):
        self.assertNotIn("04h", H); self.assertNotIn("10h · 16h", H)
        self.assertIn("o próximo voo decola em segundos", H)
