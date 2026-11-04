"""R44 (titular, 05/11/2026): o catálogo das oportunidades conhecidas (captacao-*) nunca sai do sistema."""
from pathlib import Path


def test_o_catalogo_nao_e_expurgado():
    b = Path("eldorado/base/comandante/biblioteca.py").read_text(encoding="utf-8")
    assert 'str(x["id"]).startswith("captacao-")' in b
    a = Path("eldorado/base/cartorio/analise_externa.py").read_text(encoding="utf-8")
    assert 'if v.decisao == "descartar" and str(v.livro_id).startswith("captacao-"):' in a and 'decisao="arquivar"' in a


def test_as_edicoes_anteriores_viram_previsao():
    from eldorado.base.cartorio.analise_externa import Veredito, _prever_pelas_edicoes
    ev = []

    class D:
        def emitir(self, t, m, d):
            ev.append((t, d))
    _prever_pelas_edicoes(Veredito(livro_id="captacao-001", decisao="valido",
                                   edicoes_anteriores=["2024-03-10", "2025-03-15", "2026-03-12"]), D())
    assert ev and ev[0][0] == "previsao.calculada" and ev[0][1]["proxima_abertura_prevista"][5:7] == "03" and ev[0][1]["confianca"] >= 0.75
