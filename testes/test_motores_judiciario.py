"""Os motores do Judiciário nas páginas reais gravadas (diagnóstico de 23/10/2026)."""
from paginas_servidor import motor, servir


def test_cnj_entrega_o_edital_da_comarca_e_veta_o_ruido(tmp_path):
    srv, base = servir("judiciario-sondagem", ["https://www.cnj.jus.br"])
    try:
        m = motor("judiciario-cnj", base, ["https://www.cnj.jus.br"], tmp_path)
        pistas = m._descobrir(m.cfg.fonte[0]) or []
        passam = [p.titulo for p in pistas if m._passa_lexico(p.titulo, "")]
        assert "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária" in passam   # 'recursos' não é 'curso'
        assert not [t for t in passam if "encontro de apenados" in t or t.lower().startswith("continue lendo")]
    finally:
        srv.shutdown()
