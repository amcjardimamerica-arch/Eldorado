"""02/11/2026 (titular): a Sala de controle com o mesmo fundo do calendário e das Oportunidades abertas — o céu estrelado."""
from pathlib import Path

CEU = "radial-gradient(ellipse 60% 60% at 38% 48%,#1E2742 0,#121A31 42%,#0A0F1F 78%,#070A15 100%)"


def test_a_sala_tem_o_ceu_do_calendario():
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert f"body:has(#v-neural:not(.oculto)){{background:{CEU} fixed}}" in p
    assert f"body:has(#v-editais:not(.oculto)){{color:#f0e2c0;background:{CEU} fixed}}" in p and CEU in p.split("#sj .estrelas{")[0]
    assert '<canvas class="ceu-sj" id="nv-estrelas"' in p and 'ceuEm("nv-estrelas","v-neural")' in p
    assert "#2A2470 0,transparent 60%" not in p and "for(const s of FUNDO)" not in p   # sem as nebulosas e os pontos fixos antigos
