"""05/11/2026 (titular): o Mapa de oportunidades da Bússola — os dias com as novas, todas as abertas no mapa, a cobertura
em dias e a telemetria das leituras dos motores."""
from pathlib import Path

from eldorado.base.cerebro.regencia import _telemetria


def test_a_telemetria_pelo_relatorio_do_motor():
    rel = ["DOU — seção 3: 12 pista(s), 4 achado(s)", "DOU — extra: sem mudança desde a última leitura",
           "DOU — seção 1: não lida (Bloqueado)", "alvo X: mudou (2 achado(s))"]
    assert _telemetria(rel) == {"fontes_lidas": 3, "mudancas": 2, "bloqueios": 1}


def test_o_mapa_le_os_dias_e_mostra_todas_as_abertas():
    leg = Path("eldorado/base/painel/legado.py").read_text(encoding="utf-8")
    assert '"dias": {d: _dia_do_mapa(d, lst, primeira)' in leg and '"total": len(novos), "reapresentados": reap' in leg
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "!UF_BR.has(e.uf)" in h
    d = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert 'if k in v["cats"] and v["novas"]' in d
