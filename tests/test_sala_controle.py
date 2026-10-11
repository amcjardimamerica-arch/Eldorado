"""11/10/2026 (titular): sala de controle da rede neural — cada função num instrumento com as quatro respostas (o que faz,
quando, efeito, resultado), estado pela cadência e pela faixa, anunciadores, mímico e página no Eldorado."""
import json, sys, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import sala_controle as S


class TesteEstado(unittest.TestCase):
    def test_estados(self):
        self.assertEqual(S._estado(None, 2, None, None)[0], "cinza")
        self.assertEqual(S._estado(0.5, 2, 0.9, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "verde")
        self.assertEqual(S._estado(0.5, 2, 0.75, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "amarelo")
        self.assertEqual(S._estado(0.5, 2, 0.6, {"normal": [0.8, None], "alarme": [0.7, None]})[0], "vermelho")
        self.assertEqual(S._estado(10, 2, 0.9, None)[0], "vermelho", "parado há mais de 3× a cadência")
        self.assertEqual(S._estado(3, 2, 0.9, None)[0], "amarelo")

    def test_montar_com_dados_reais(self):
        r = S.montar()
        self.assertGreaterEqual(len(r["instrumentos"]), 18)
        for x in r["instrumentos"]:
            for k in ("faz", "efeito", "resultado", "estado", "sub", "nome"):
                self.assertIn(k, x, f"{x['id']} sem {k}")
        self.assertTrue(0 <= (r["indice_saude"] or 0) <= 100)
        self.assertEqual(len(r["mimico"]), 8)

    def test_pagina_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('id="v-neural"', h); self.assertIn('"neural"]', h); self.assertIn('data-v="neural"', h)
        self.assertIn("window.desenhaNeural", h); self.assertIn("sala_controle.json", h)
        self.assertIn("python -m src.sala_controle", (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "docs/prompts/PROMPT-SALA-DE-CONTROLE-REDE-NEURAL-2026-10-11.md").exists())
        # v3 (11/10): a constelação — desktop, largura total, céu em canvas (as estrelas de dados são os motores), nove etapas
        # ligadas por sinapses, janela-holograma no centro que nasce do elemento clicado (nunca painel lateral)
        for marca in ('id="nv-ceu"', "const ETAPAS=[", "window.nvHolo", 'class="holo"', "width:100vw", "prefers-reduced-motion", "IntersectionObserver"):
            self.assertIn(marca, h)
        sec = h[h.index('<section id="v-neural"'):h.index("</section>", h.index('<section id="v-neural"'))]
        self.assertNotIn('class="detalhe"', sec, "o detalhe não abre em painel lateral")
        self.assertEqual(sec.count("<canvas"), 1, "um único canvas para o céu")
        self.assertTrue((ROOT / "docs/prompts/PROMPT-SALA-DE-CONTROLE-CONSTELACAO-2026-10-11.md").exists())
        self.assertIn('"detalhes"', (ROOT / "src/sala_controle.py").read_text(encoding="utf-8"))
        # ajustes de 11/10: página estática (sem deslocamento na rolagem nem inclinação), luzes de estrela (vermelha cintila),
        # ponteiros vivos, janela no corpo da página (sempre enquadrada), listas do sistema nervoso clicáveis e de mesma altura
        self.assertNotIn("--sy", sec, "sem paralaxe na rolagem"); self.assertNotIn("rotateY(var(--ry", sec, "sem inclinação")
        for marca in ("@keyframes cintila", ".luz.vermelho", 'class="vivo"', "function vivos(", 'P.id="nv-portal"', "window.nvFluxo", 'class="rol"', "offsetWidth"):
            self.assertIn(marca, sec, marca)
        # rolagem fluida (11/10): sem desfoque sobre o céu animado, brilhos pré-desenhados, céu a 30 quadros, ponteiros sem medir a tela
        self.assertNotIn("backdrop-filter:blur(5px)", sec); self.assertIn("function sprite(", sec); self.assertIn("t-ultimoQuadro<32", sec)
        self.assertIn("IntersectionObserver(es=>es.forEach(en=>{ en.target.querySelectorAll(\".vivo\")", sec)
        self.assertNotIn("g.ownerSVGElement.getBoundingClientRect()", sec)
        self.assertIn("if(!_rolou && Math.abs(window.scrollY-_y)>2) window.scrollTo(0,_y);", h, "a atualização não puxa a página de volta")
        # constelações reais (uma por etapa, sem repetir), estrelas de erro em todas as etapas, janela que não some ao reabrir
        nomes = ["Lira", "Virgem", "Ursa Maior", "Sagitário", "Ursa Menor", "Libra", "Órion", "Cruzeiro do Sul", "Carina"]
        for nome in nomes:
            self.assertEqual(sec.count(f'nome:"{nome}"'), 1, nome)
        self.assertIn("estrelas de ERRO", sec); self.assertIn("clearTimeout(H._tFecha)", sec); self.assertIn("H._sessao===sessao", sec)
        # toda caixa com dado responde ao clique; nomes das constelações só na janela (não no céu)
        for marca in ('data-det="motor|', 'data-det="maestro|', 'data-det="hist|', 'data-det="missao|', 'data-det="familia|', 'data-det="item|',
                      '"passo"', '"etapa"', '"estante"', '"origem"', '"reproc"', "function detalheItem(", "function ligarDetalhes(", "window.nvVisao", 'class="cabeca-const"', "function desenhoConst("):
            self.assertIn(marca, sec, marca)
        self.assertNotIn("g.fillText(no.nome", sec, "nomes das constelações ocultos no céu")
        # nome da página (11/10): "Rede Neural"
        self.assertIn('<button data-v="neural">Rede Neural</button>', h); self.assertIn("<h2>Rede Neural</h2>", h)
        self.assertNotIn(">Sala de controle<", h)
        g = (ROOT / "src/sala_controle.py").read_text(encoding="utf-8")
        self.assertIn('"ultimas"', g); self.assertIn('{"id": x["id"], "quando"', g)


if __name__ == "__main__":
    unittest.main()
