"""O ranking de empresas (titular, 25/10/2026: a aba estava zerada)."""
import sqlite3

from eldorado.base.painel.dados import _molde
from eldorado.base.painel.ranking import montar


def test_o_ranking_tem_todas_as_empresas_da_biblioteca():
    con = sqlite3.connect("file:dados/biblioteca.db?mode=ro", uri=True)
    r = montar(con, _molde)
    n = con.execute("SELECT COUNT(*) FROM empresa").fetchone()[0]
    assert r["total"] == n == len(r["empresas"]) > 0                                      # todas as empresas, nenhuma de fora
    assert r["listas"]["destinacao_tributaria"]["total"] + r["listas"]["patrocinio_privado"]["total"] == n
    trib = [e for e in r["empresas"] if e["origem"] == "destinação tributária"]
    assert [e["n_na_lista"] for e in trib] == list(range(1, len(trib) + 1))                 # as posições em ordem
    assert all(trib[i]["pontos_lista"] >= trib[i + 1]["pontos_lista"] for i in range(len(trib) - 1))
    assert all(e["pontuacao"]["porque"] for e in r["empresas"]) and r["catalogo_de_leis"]


def test_a_importacao_das_empresas_do_eldorado0_unifica_pelo_cnpj(bancos, gravador, diario, tmp_path):
    """25/10/2026: as empresas do Eldorado0 unificadas às da Biblioteca: o que existe prevalece; o que falta se completa."""
    from eldorado.base.especial.importar_e0 import importar
    from eldorado.base.nucleo.eventos import criar, ler
    assert gravador.aplicar([criar("empresa.registrada", "t", {"cnpj": "11222333000144", "razao_social": "Empresa da Biblioteca", "uf": "GO",
                                                                "descoberta_por": "motor", "descoberta_em": "2026-10-20", "atualizada_em": "2026-10-20"})]).ok
    e0 = {"empresas": [{"nome": "EMPRESA E0", "cadastro": {"cnpj": "11.222.333/0001-44", "razao_social": "Outro nome", "site": "https://e.com.br"},
                        "programas": [{"chave": "rouanet", "verificado": True, "prova": "Salic 2024"}], "salic": {"total": 5000.0}, "origem": "destinação tributária"},
                       {"nome": "NOVA", "cadastro": {"cnpj": "99888777000166"}, "programas": [{"chave": "pat", "verificado": True}]}]}
    conta = importar(bancos["biblioteca"], e0, diario)
    assert conta == {"empresas": 2, "novas": 1, "completadas": 1, "incentivos": 2, "sem_cnpj": 0}
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    b = bancos["biblioteca"]
    assert tuple(b.execute("SELECT razao_social, site FROM empresa WHERE cnpj = '11222333000144'").fetchone()) == ("Empresa da Biblioteca", "https://e.com.br")
    assert tuple(b.execute("SELECT valor, comprovado FROM incentivo WHERE cnpj = '11222333000144' AND lei = 'Rouanet'").fetchone()) == (5000.0, 1)
