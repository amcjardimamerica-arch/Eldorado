"""02/11/2026 (titular): a sobrecarga tem a marca de ciência (retirada manual); o expurgo e a pesquisa pelo Claude no
Chrome só alertam acima de 50 itens ou com o pendente mais antigo há mais de 168 horas (1 semana)."""
from pathlib import Path

from eldorado.base.painel.sala import _alerta_claude


def test_expurgo_e_chrome_so_acima_de_50_ou_de_uma_semana():
    assert _alerta_claude(0, None) == "verde" and _alerta_claude(50, 10) == "verde" and _alerta_claude(45, 167) == "verde"
    assert _alerta_claude(51, 1) == "amarelo" and _alerta_claude(45, 189) == "amarelo" and _alerta_claude(None, None) == "cinza"


def test_a_sobrecarga_tem_a_marca_de_ciencia():
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "Ciente — retirar o alerta" in h and "SC=filtraCientes(await r.json())" in h and "SC=filtraCientes(novo)" in h
    assert "nvAlerta('${e(j.id)}',this)" in h
