"""O avião do Piloto: só sobre o lugar exato do trabalho (24/09). O posto em duas páginas (22/09)."""
import pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
H = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")


class TesteAviaoSoNoLugarExato(unittest.TestCase):
    """24/09, por ordem do titular: o avião é a imagem ORIGINAL, sem redução, e vai e volta por
    cima do motor da Bússola em que o Piloto está trabalhando, como sinal de alerta. Nenhuma
    outra parte do site recebe o avião."""

    def test_a_imagem_e_o_arquivo_original_sem_reducao(self):
        img = ROOT / "docs/img/aviao-amc.webp"
        self.assertEqual(img.stat().st_size, 1643100)                 # o arquivo enviado, byte a byte
        self.assertFalse((ROOT / "docs/img/aviao-amc-parado.webp").exists())
        self.assertIn('<img src="img/aviao-amc.webp"', H)

    def test_so_nos_motores_da_bussola(self):
        self.assertIn('#mt-lista .mt-item[data-id="${_ce(m.motor)}"]', H)
        self.assertIn("SÓ OS MOTORES DA BÚSSOLA", H)
        self.assertNotIn(".pil-resg-l[data-id=", H.split("window.lugarDoTrabalho")[1][:900])

    def test_a_travessia_antiga_e_a_patrulha_sairam(self):
        for velho in ("pousarAviaoErrante", "ONDE_POUSAR", "@keyframes pil-travessia",
                      "patrulha a última faixa", "zonaDeVoo", "novoDestino"):
            self.assertNotIn(velho, H, velho)

    def test_vai_e_volta_por_cima_do_motor(self):
        self.assertIn("function corredor(el)", H)
        self.assertIn("y:y0-AV_T*.62", H)                            # por cima do topo do motor
        self.assertIn("AV.x+=AV.dir*200*dt;", H)
        self.assertIn("meia-volta na borda", H)
        self.assertIn("nunca fora do motor", H)

    def test_o_nariz_aponta_para_onde_vai(self):
        self.assertIn('AV.el.firstElementChild.style.transform=AV.esq?"scaleX(-1)":"none"', H)

    def test_sem_missao_ou_posicao_vencida_nao_aparece(self):
        self.assertIn('if(!P||P.estado!=="em_voo"||!P.missao) return false;', H)
        self.assertIn("if(!posicaoValida(P)){ pousarAviao(); return; }", H)

    def test_a_posicao_vem_do_ramo_ao_vivo(self):
        self.assertIn("contents/docs/dados/piloto_posicao.json?ref=piloto-ao-vivo", H)
        self.assertIn("raw.githubusercontent.com/amcjardimamerica-arch/Eldorado/piloto-ao-vivo", H)
        self.assertIn("r.status===403||r.status===429", H)

    def test_para_com_o_mouse_e_respeita_menos_movimento(self):
        self.assertIn('d.addEventListener("mouseenter",()=>{AV.pausaAte=Infinity;});', H)
        self.assertIn("if(AV.reduz){", H)


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
        self.assertIn("o próximo decola em segundos", H)   # a frase do rodapé foi absorvida pelo bloco ao vivo
