"""R46 (titular, 05/11/2026): uma régua só, do banco — validada é a aberta no Farol; em verificação, a aberta na esteira."""
from pathlib import Path


def test_uma_regua_para_abertas_validadas_e_em_verificacao():
    s = Path("eldorado/base/painel/dados.py").read_text(encoding="utf-8")
    assert 'conf = r["fase"] == "farol"' in s and 'estado="validada" if conf else "em verificação"' in s
    assert '"validadas": sum(1 for r in livros if r["fase"] == "farol")' in s
    assert '"em_verificacao": sum(1 for r in livros if r["fase"] != "farol")' in s
    assert 'val_ct.get("aprovado", 0),\n            "em_verificacao"' not in s


def test_o_arquivado_por_decisao_nao_volta_a_recepcao():
    """05/11/2026: a devolução automática do arquivo trazia de volta à recepção os livros arquivados pelo veredito do
    Chrome (encerrada, arquivar) e os sem data — 40 livros já verificados voltavam à esteira."""
    import sqlite3

    from eldorado.base.cartorio.auditoria import devolver_abertas_do_arquivo
    c = sqlite3.connect(":memory:")
    c.executescript(
        "CREATE TABLE passaporte(livro_id TEXT, fase TEXT, entrou_em TEXT);"
        "CREATE TABLE livro_dados(livro_id TEXT, situacao_prazo TEXT, inscricao_fim TEXT);"
        "CREATE TABLE passagem(livro_id TEXT, de TEXT, para TEXT, em TEXT, autorizado_por TEXT, motivo TEXT);"
        "INSERT INTO passaporte VALUES ('A','arquivo','2026-11-05'),('B','arquivo','2026-11-05'),('C','arquivo','2026-11-05');"
        "INSERT INTO livro_dados VALUES ('A','aberta','2099-01-01'),('B','aberta',NULL),('C','aberta','2099-01-01');"
        "INSERT INTO passagem VALUES ('A','certificacao','arquivo','2026-11-05','x','a análise externa decidiu «encerrada»'),"
        "('B','preparacao','arquivo','2026-11-05','x','o prazo encerrou'),('C','preparacao','arquivo','2026-11-05','x','o prazo encerrou');")
    movidos = []

    class P:
        def __init__(self, *a, **k):
            pass

        def mover(self, lid, para, motivo, extra):
            movidos.append(lid)
            return True, ""
    import eldorado.base.cartorio.passaporte as PS
    orig = PS.Passaporte
    PS.Passaporte = P
    try:
        devolver_abertas_do_arquivo(c, None)
    finally:
        PS.Passaporte = orig
    assert movidos == ["C"]          # A: arquivado pelo Chrome; B: sem data — ficam; C: arquivado por prazo, reabriu — volta
