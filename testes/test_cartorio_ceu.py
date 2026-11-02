"""02/11/2026 (titular): o Cartório sob o mesmo céu estrelado das outras etapas — só o fundo; os painéis como estão."""
from pathlib import Path

P = Path("eldorado/base/painel/pagina")


def test_o_cartorio_tem_o_ceu_das_outras_etapas():
    h = (P / "dashboard.html").read_text(encoding="utf-8")
    assert "body:has(#v-cartorio:not(.oculto)){background:radial-gradient(ellipse 60% 60% at 38% 48%,#1E2742 0,#121A31 42%,#0A0F1F 78%,#070A15 100%) fixed}" in h
    assert '<canvas class="ca-ceu" id="ca-estrelas"' in h and 'ceuEm("ca-estrelas","v-cartorio")' in h
    assert "#cl2,#cl3,#cl4{background:transparent!important" in h
    assert '"v-cartorio"' in (P / "amc-menu.js").read_text(encoding="utf-8").split("ESCURAS=")[1][:120]
